# Nichtlineare Z-Stauchung der Relief-Spitzen von binaeren STLs (Untersetzer-Vorbereitung).
# Prinzip Soft-Knee-Kompressor: unterhalb der Knie-Hoehe K bleibt alles unveraendert,
# darueber werden Hoehen weich gegen eine Decke C gestaucht:
#     z' = K + (C-K) * tanh((z-K)/(C-K))
# -> am Knie stetig differenzierbar (Steigung 1), Spitzen buendeln sich knapp unter C.
# Reine Vertex-Verschiebung (monoton), kein Boolean -> robust auch bei Meshy-Topologie.
# Ergebnis danach im Slicer mit Schnittebene pruefen und ggf. minimal kappen.
#
# Aufruf:
#   python _compress_z.py                                # alle *_cut2.stl im Skriptordner, Auto-Parameter
#   python _compress_z.py datei.stl --knee 9 --ceiling 10.5   # manuell nachjustieren
# Auto-Parameter pro Datei:
#   Knie    = P75 der Oberseiten-Heightmap (25 % der Flaeche liegen darueber)
#   Ceiling = Knie + max(0.8 mm, 15 % von (zmax - Knie))
# Hoehenangaben relativ zur Unterkante der Hochachse (bei diesen Dateien: z=0).
# Ausgabe: <name>_soft.stl neben der Eingabedatei.
import argparse
import glob
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _analyze_z import GRID, read_binary_stl


def top_heightmap(verts, up, axes, mn, dims):
    z = verts[:, up] - mn[up]
    ix = np.clip(((verts[:, axes[0]] - mn[axes[0]]) / dims[axes[0]] * (GRID - 1)).astype(int), 0, GRID - 1)
    iy = np.clip(((verts[:, axes[1]] - mn[axes[1]]) / dims[axes[1]] * (GRID - 1)).astype(int), 0, GRID - 1)
    hm = np.full(GRID * GRID, -np.inf, dtype=np.float32)
    np.maximum.at(hm, ix * GRID + iy, z.astype(np.float32))
    return hm[hm > -np.inf]


def band_fracs(top):
    zmax = top.max()
    return zmax, {d: float((top >= zmax - d).sum() / top.size * 100) for d in (0.2, 0.5, 1.0)}


def write_binary_stl(path, tris, note=""):
    dt = np.dtype([
        ("normal", np.float32, (3,)),
        ("v", np.float32, (3, 3)),
        ("attr", np.uint16),
    ])
    rec = np.zeros(len(tris), dtype=dt)
    rec["v"] = tris
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    rec["normal"] = np.divide(n, ln, out=np.zeros_like(n), where=ln > 0)
    with open(path, "wb") as f:
        f.write(note.encode("ascii", "replace")[:80].ljust(80, b" "))
        f.write(np.uint32(len(tris)).tobytes())
        rec.tofile(f)


def compress(path, knee=None, ceiling=None):
    verts = read_binary_stl(path).astype(np.float64)
    mn, mx = verts.min(axis=0), verts.max(axis=0)
    dims = mx - mn
    up = int(np.argmin(dims))  # flachste Achse = Hochachse
    axes = [a for a in range(3) if a != up]

    top = top_heightmap(verts, up, axes, mn, dims)
    zmax = float(top.max())
    if knee is None:
        knee = float(np.percentile(top, 75.0))
    if ceiling is None:
        ceiling = knee + max(0.8, 0.15 * (zmax - knee))
    if not (0 < knee < zmax and ceiling > knee):
        raise SystemExit(f"{os.path.basename(path)}: ungueltige Parameter (Knie {knee:.2f}, Ceiling {ceiling:.2f}, zmax {zmax:.2f})")
    span = ceiling - knee

    z = verts[:, up] - mn[up]
    znew = np.where(z > knee, knee + span * np.tanh((z - knee) / span), z)
    verts[:, up] = znew + mn[up]

    out_path = os.path.splitext(path)[0] + "_soft.stl"
    write_binary_stl(out_path, verts.reshape(-1, 3, 3).astype(np.float32),
                     f"z-soft-compressed knee={knee:.2f} ceiling={ceiling:.2f}")

    # Band-Statistik: Heightmap-Werte durch dieselbe monotone Abbildung schicken
    top_new = np.where(top > knee, knee + span * np.tanh((top - knee) / span), top)
    _, before = band_fracs(top)
    zmax_new, after = band_fracs(top_new)

    print(f"\n=== {os.path.basename(path)} -> {os.path.basename(out_path)} ===")
    print(f"  Hochachse {'XYZ'[up]}, Hoehe {zmax:.2f}, betroffene Flaeche (ueber Knie): {(top > knee).sum() / top.size * 100:.0f} %")
    print(f"  Knie {knee:.2f} / Ceiling {ceiling:.2f} (Span {span:.2f})")
    print(f"  Neue Gesamthoehe: {zmax_new:.2f}  ({zmax_new - zmax:+.2f})")
    print(f"  Flaeche im obersten Band (vorher -> nachher):")
    for d in (0.2, 0.5, 1.0):
        print(f"    {d:.1f}-Band: {before[d]:5.1f} % -> {after[d]:5.1f} %")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Nichtlineare Z-Stauchung der Relief-Spitzen (Soft-Knee).")
    ap.add_argument("files", nargs="*", help="STL-Dateien (Default: alle *_cut2.stl im Skriptordner)")
    ap.add_argument("--knee", type=float, help="Knie-Hoehe (Default: P75 der Oberseiten-Heightmap)")
    ap.add_argument("--ceiling", type=float, help="Decken-Hoehe (Default: Knie + max(0.8, 0.15*(zmax-Knie)))")
    args = ap.parse_args()
    files = args.files or sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "*_cut2.stl")))
    if not files:
        raise SystemExit("keine STL-Dateien gefunden")
    for p in files:
        compress(p, knee=args.knee, ceiling=args.ceiling)
