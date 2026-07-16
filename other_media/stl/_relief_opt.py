# Adaptive Relief-Optimierung fuer Untersetzer-STLs (Base/Detail-Zerlegung + lokale
# Detail-Normalisierung, Bas-Relief-Prinzip).
#
# Pipeline pro STL:
#   1. Oberseiten-Heightmap H (512^2), Loecher/Rand per Naechster-Nachbar gefuellt.
#   2. Basis B = Median-Filter (Fenster 2*--r-detail): folgt breiten Strukturen,
#      schmale Grate UND schmale Gravuren wandern beide ins Detail D = H - B.
#   3. Basis-Remap f(B): unter Hintergrund bg Identitaet, darueber tanh-Saettigung
#      Richtung Plateau P -> mittlere Sockel werden ANGEHOBEN, hohe ABGESENKT.
#   4. Detail-Normalisierung: lokale Detail-Maxima werden auf gemeinsame Amplitude
#      --d-ceil skaliert (Auto-Gain, Kappung max 2x) -> alle Detailspitzen liegen
#      koplanar bei P + d-ceil, Gravuren bleiben als Vertiefungen erhalten.
#   5. Optional --img-detail: wo das Mesh kein Detail hat, wird Hochpass-Detail aus
#      der PNG-Vorlage ins Plateau gepraegt (Orientierung per Kanten-Korrelation).
#   6. Versatzfeld O spaltenweise auf die Vertices (bilinear), z-Rampe haelt
#      Unterseite/Grundplatte fest. Keine Booleans -> Meshy-Topologie egal.
#
# Aufruf:
#   python _relief_opt.py                        # alle *_cut2.stl, sucht <gott>.png daneben
#   python _relief_opt.py slaanesh_cut2.stl --plateau 0.5 --d-ceil 1.0 --img-detail 0.4
# Ausgabe: <name>_opt.stl + <name>_opt_preview.png (Schattierung vorher|nachher)
import argparse
import glob
import os
import re
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _analyze_z import read_binary_stl

G = 512  # Heightmap-Aufloesung


def heightfield(verts, up, axes, mn, dims):
    """Max-z-Heightmap [x,y], Occupancy und Footprint-Maske; Werte ausserhalb der
    Occupancy (auch ausserhalb des Footprints) per Naechster-Nachbar fortgesetzt."""
    z = verts[:, up] - mn[up]
    ix = np.clip(((verts[:, axes[0]] - mn[axes[0]]) / dims[axes[0]] * (G - 1)).astype(int), 0, G - 1)
    iy = np.clip(((verts[:, axes[1]] - mn[axes[1]]) / dims[axes[1]] * (G - 1)).astype(int), 0, G - 1)
    hm = np.full(G * G, -np.inf, dtype=np.float64)
    np.maximum.at(hm, ix * G + iy, z)
    hm = hm.reshape(G, G)
    occ = np.isfinite(hm)
    fp = ndimage.binary_fill_holes(ndimage.binary_closing(occ, np.ones((5, 5))))
    _, idx = ndimage.distance_transform_edt(~occ, return_indices=True)
    filled = hm[idx[0], idx[1]]  # ueberall definiert (auch ausserhalb fp fortgesetzt)
    return filled, occ, fp


def median_base(H, r_px):
    """Median-Basis auf halbierter Aufloesung (Tempo), bilinear zurueckskaliert."""
    H2 = H[::2, ::2]
    size = max(3, int(round(r_px)) | 1)  # Fenster ~2r auf halber Aufloesung
    B2 = ndimage.median_filter(H2, size=size, mode="nearest")
    B = ndimage.zoom(B2, (H.shape[0] / B2.shape[0], H.shape[1] / B2.shape[1]), order=1)
    return B[:H.shape[0], :H.shape[1]]


def load_image_grid(png_path, fp):
    """PNG-Vorlage laden, Vordergrund-BBox auf die Footprint-BBox der Heightmap
    resamplen und ins [x,y]-Grid der Heightmap drehen."""
    img = Image.open(png_path).convert("RGB")
    arr = np.asarray(img, dtype=np.float64)
    L = arr.mean(axis=2)
    sat = arr.max(axis=2) - arr.min(axis=2)
    fg = (L < 235) | (sat > 25)
    rows = np.where(fg.any(axis=1))[0]
    cols = np.where(fg.any(axis=0))[0]
    img_c = img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))

    xs = np.where(fp.any(axis=1))[0]
    ys = np.where(fp.any(axis=0))[0]
    nx, ny = xs[-1] - xs[0] + 1, ys[-1] - ys[0] + 1
    img_r = img_c.resize((nx, ny), Image.LANCZOS)
    a = np.asarray(img_r.convert("L"), dtype=np.float64)[::-1, :].T  # -> [x,y]
    grid = np.zeros((G, G))
    grid[xs[0]:xs[0] + nx, ys[0]:ys[0] + ny] = a
    return grid


def grad_mag(a, sigma):
    gx, gy = np.gradient(ndimage.gaussian_filter(a, sigma))
    return np.hypot(gx, gy)


def best_flip(img_grid, H, fp):
    """Spiegelungs-Varianten testen: Korrelation der Kantenbilder."""
    Hg = grad_mag(H, 2)[fp]
    best, best_c, best_name = img_grid, -2.0, "?"
    for name, g in [("original", img_grid), ("flip-x", img_grid[::-1, :]),
                    ("flip-y", img_grid[:, ::-1]), ("flip-xy", img_grid[::-1, ::-1])]:
        c = np.corrcoef(grad_mag(g, 2)[fp], Hg)[0, 1]
        if c > best_c:
            best, best_c, best_name = g, c, name
    return best, best_c, best_name


def shade(H, fp, px_per_mm):
    """Einfache Lambert-Schattierung der Heightmap (Slicer-aehnlicher Eindruck)."""
    gx, gy = np.gradient(H, 1.0 / px_per_mm)
    n = np.dstack([-gx, -gy, np.ones_like(H)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    light = np.array([-0.5, -0.5, 0.8])
    light /= np.linalg.norm(light)
    lam = np.clip(n @ light, 0, 1)
    img = (40 + 215 * lam) * fp
    return np.flipud(img.T).astype(np.uint8)  # [x,y] -> Bildzeilen (y nach unten)


def write_binary_stl(path, tris, note=""):
    dt = np.dtype([("normal", np.float32, (3,)), ("v", np.float32, (3, 3)), ("attr", np.uint16)])
    rec = np.zeros(len(tris), dtype=dt)
    rec["v"] = tris
    nrm = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ln = np.linalg.norm(nrm, axis=1, keepdims=True)
    rec["normal"] = np.divide(nrm, ln, out=np.zeros_like(nrm), where=ln > 0)
    with open(path, "wb") as f:
        f.write(note.encode("ascii", "replace")[:80].ljust(80, b" "))
        f.write(np.uint32(len(tris)).tobytes())
        rec.tofile(f)


def band_fracs(top):
    zref = float(np.percentile(top, 99.8))  # robuste Referenzhoehe statt Einzelzellen-Maximum
    return zref, {d: float((top >= zref - d).sum() / top.size * 100) for d in (0.2, 0.5, 1.0)}


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def process(path, args):
    name = os.path.basename(path)
    verts = read_binary_stl(path).astype(np.float64)
    mn, mx = verts.min(axis=0), verts.max(axis=0)
    dims = mx - mn
    up = int(np.argmin(dims))
    axes = [a for a in range(3) if a != up]
    px_per_mm = (G - 1) / float(max(dims[axes[0]], dims[axes[1]]))

    H, occ, fp = heightfield(verts, up, axes, mn, dims)
    zmax = float(H[fp].max())

    # Hintergrund-Niveau: Modalwert der unteren Haelfte (0.25-mm-Bins)
    vals = H[fp]
    lower = vals[vals <= np.median(vals)]
    hist, edges = np.histogram(lower, bins=max(8, int(np.ptp(lower) / 0.25)))
    bg = args.bg if args.bg is not None else float((edges[np.argmax(hist)] + edges[np.argmax(hist) + 1]) / 2)

    # 2. Base/Detail-Zerlegung (Median-Basis)
    B = median_base(H, args.r_detail * px_per_mm)
    D = H - B

    # 3. Basis-Remap: ab t >= --sat der Basishoehe liegt die Basis EXAKT auf dem
    # Plateau (echte Ebene), darunter weicher Anstieg (Smoothstep)
    Bmax = float(B[fp].max())
    P = args.plateau_mm if args.plateau_mm is not None else bg + args.plateau * (zmax - bg)
    t = (B - bg) / max(Bmax - bg, 1e-9)
    fB = np.where(B > bg, bg + (P - bg) * smoothstep(t / args.sat), B)

    # 4. Detail-Normalisierung: lokale Maxima -> gemeinsame Amplitude d_ceil
    dC = args.d_ceil
    env_px = max(3, int(round(args.r_detail * px_per_mm)) | 1)
    Dpos = np.maximum(D, 0)
    Dloc = ndimage.gaussian_filter(ndimage.grey_dilation(Dpos, size=(env_px, env_px)), env_px / 2.5)
    Dloc = np.maximum(Dloc, Dpos)
    scale = dC / np.maximum(Dloc, dC / 2.0)  # implizite Kappung: max 2x Verstaerkung
    # Verstaerkung (>1) nur wo echtes Detail vorliegt, sonst wuerde Rauschen verdoppelt
    scale = 1.0 + (scale - 1.0) * np.where(scale > 1.0, smoothstep(Dloc / (0.5 * dC)), 1.0)
    Dn = D * scale

    O = (fB - B) + (Dn - D)
    if args.mode == "inset":
        # Detail ins Plateau einlassen: lokale (normalisierte) Detailspitzen buendig
        # mit P, Rest vertieft; Zonen ohne Detail bleiben unverschoben auf P
        w_plateau = np.clip((fB - bg) / max(P - bg, 1e-9), 0, 1)
        O -= np.clip(Dloc * scale, 0, dC) * w_plateau

    # 5. optional: Bilddetail ins Plateau praegen, wo das Mesh kaum Detail hat
    img_note = "kein Bild"
    png = args.png or re.sub(r"_cut\d*(_soft)?\.stl$", ".png", path)
    if os.path.exists(png):
        grid = load_image_grid(png, fp)
        grid, corr, flip = best_flip(grid, H, fp)
        img_note = f"{os.path.basename(png)} ({flip}, Kanten-r={corr:.2f})"
        if args.img_detail > 0:
            if corr < 0.15:
                print(f"  WARNUNG: Bildkorrelation nur {corr:.2f} - --img-detail wird uebersprungen")
            else:
                Dimg = grid - ndimage.gaussian_filter(grid, args.img_sigma_mm * px_per_mm)
                Dimg /= max(np.percentile(np.abs(Dimg[fp]), 95), 1e-9)  # -> ca. [-1..1]
                w_plateau = np.clip((fB - bg) / max(P - bg, 1e-9), 0, 1)
                w_gap = 1.0 - np.clip(Dloc / dC, 0, 1)  # nur wo Mesh-Detail fehlt
                O += args.img_detail * np.clip(Dimg, -1.5, 1.5) * w_plateau * w_gap

    O = np.nan_to_num(O * fp)

    # 6. Versatz auf Vertices anwenden, z-Rampe haelt Boden/Grundplatte fest
    z = verts[:, up] - mn[up]
    x = (verts[:, axes[0]] - mn[axes[0]]) / dims[axes[0]] * (G - 1)
    y = (verts[:, axes[1]] - mn[axes[1]]) / dims[axes[1]] * (G - 1)
    o = ndimage.map_coordinates(O, [x, y], order=1, mode="nearest")
    z0, z1 = 0.35 * bg, bg + max(1.0, 0.1 * (zmax - bg))
    w = smoothstep((z - z0) / max(z1 - z0, 1e-9))
    verts[:, up] = mn[up] + z + w * o

    suffix = "_opt.stl" if args.mode == "raise" else "_opt-inset.stl"
    out_path = os.path.splitext(path)[0].replace("_cut2", "") + suffix
    write_binary_stl(out_path, verts.reshape(-1, 3, 3).astype(np.float32),
                     f"relief-opt bg={bg:.2f} P={P:.2f} dC={dC}")

    # Statistik + Vorschau
    Hn = np.where(fp, H + O, H)
    _, before = band_fracs(H[occ])
    zmax_n, after = band_fracs(Hn[occ])
    pv = np.concatenate([shade(H, fp, px_per_mm), shade(Hn, fp, px_per_mm)], axis=1)
    pv_path = os.path.splitext(out_path)[0] + "_preview.png"
    Image.fromarray(pv).save(pv_path)

    print(f"\n=== {name} -> {os.path.basename(out_path)} ===")
    print(f"  Hintergrund {bg:.2f} / Plateau {P:.2f} / r-detail {args.r_detail} mm / d-ceil {dC} mm / Bild: {img_note}")
    print(f"  Hoehe (max): {zmax:.2f} -> {float(Hn[occ].max()):.2f}; Referenz P99.8: {zmax_n:.2f}")
    print(f"  Flaeche im Band unter Referenz (vorher -> nachher):")
    for d in (0.2, 0.5, 1.0):
        print(f"    {d:.1f}-Band: {before[d]:5.1f} % -> {after[d]:5.1f} %")
    print(f"  Vorschau: {os.path.basename(pv_path)} (links vorher, rechts nachher)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Adaptive Relief-Optimierung (Base/Detail + lokale Detail-Normalisierung).")
    ap.add_argument("files", nargs="*", help="STL-Dateien (Default: alle *_cut2.stl im Skriptordner)")
    ap.add_argument("--r-detail", type=float, default=5.0, help="Detail-Radius in mm: Schmaleres als ~2r ist Detail (Default 5)")
    ap.add_argument("--plateau", type=float, default=0.5, help="Plateau als Anteil der Reliefhoehe ueber Hintergrund (Default 0.5)")
    ap.add_argument("--plateau-mm", type=float, help="Plateau absolut in mm (ueberschreibt --plateau)")
    ap.add_argument("--sat", type=float, default=0.5, help="Basis-Anteil, ab dem exakt Plateauhoehe erreicht wird (Default 0.5)")
    ap.add_argument("--bg", type=float, help="Hintergrund-Niveau in mm (Default: automatisch)")
    ap.add_argument("--d-ceil", type=float, default=0.8, help="Ziel-Detailamplitude ueber dem Plateau in mm (Default 0.8)")
    ap.add_argument("--mode", choices=["raise", "inset"], default="raise",
                    help="raise: Detail steht ueber dem Plateau (Kontakt = Detailspitzen). inset: Detail ins Plateau eingelassen (Kontakt = Plateauflaeche, maximale Auflage)")
    ap.add_argument("--img-detail", type=float, default=0.0, help="Detail aus PNG-Vorlage in mm Amplitude einpraegen (Default 0 = aus)")
    ap.add_argument("--img-sigma-mm", type=float, default=1.5, help="Highpass-Radius fuer Bilddetail in mm (Default 1.5)")
    ap.add_argument("--png", help="Pfad zur Bildvorlage (Default: <gott>.png neben der STL)")
    args = ap.parse_args()
    files = args.files or sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "*_cut2.stl")))
    if not files:
        raise SystemExit("keine STL-Dateien gefunden")
    for p in files:
        process(p, args)
