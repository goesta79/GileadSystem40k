# Analysiert das Z-Profil der Oberseite von binaeren STL-Dateien (Untersetzer-Check).
# Aufruf: python other_media/stl/_analyze_z.py [datei.stl ...]  (ohne Argumente: alle *.stl im Skriptordner)
import sys
import glob
import os
import numpy as np

GRID = 256  # Heightmap-Aufloesung (Zellen pro Achse)


def read_binary_stl(path):
    with open(path, "rb") as f:
        f.seek(80)
        n = np.frombuffer(f.read(4), dtype=np.uint32)[0]
        dt = np.dtype([
            ("normal", np.float32, (3,)),
            ("v", np.float32, (3, 3)),
            ("attr", np.uint16),
        ])
        data = np.frombuffer(f.read(n * dt.itemsize), dtype=dt, count=n)
    return data["v"].reshape(-1, 3)  # alle Dreiecks-Eckpunkte (mit Duplikaten)


def analyze(path):
    verts = read_binary_stl(path)
    mn, mx = verts.min(axis=0), verts.max(axis=0)
    dims = mx - mn
    up = int(np.argmin(dims))  # flachste Achse = Hochachse (Relief)
    axes = [a for a in range(3) if a != up]

    z = verts[:, up] - mn[up]
    x = verts[:, axes[0]] - mn[axes[0]]
    y = verts[:, axes[1]] - mn[axes[1]]
    H = dims[up]

    # Heightmap: max z pro xy-Zelle
    ix = np.clip((x / dims[axes[0]] * (GRID - 1)).astype(int), 0, GRID - 1)
    iy = np.clip((y / dims[axes[1]] * (GRID - 1)).astype(int), 0, GRID - 1)
    flat = ix * GRID + iy
    hm = np.full(GRID * GRID, -np.inf, dtype=np.float32)
    np.maximum.at(hm, flat, z.astype(np.float32))
    occ = hm > -np.inf
    top = hm[occ]

    zmax = float(top.max())
    pct = lambda q: float(np.percentile(top, q))
    frac_within = lambda d: float((top >= zmax - d).sum() / top.size * 100)

    # Verteilung der hoechsten Punkte ueber die Flaeche (Wackel-Check):
    hm2 = hm.reshape(GRID, GRID)
    highs = np.argwhere(hm2 >= zmax - 0.3)  # Zellen im obersten 0,3-Einheiten-Band
    if len(highs) > 1:
        spread = highs.std(axis=0).mean() / GRID * 100  # % der Kantenlaenge
    else:
        spread = 0.0

    print(f"\n=== {os.path.basename(path)} ===")
    print(f"  Dreiecke: {len(verts)//3:,}")
    print(f"  Bounding Box: {dims[0]:.2f} x {dims[1]:.2f} x {dims[2]:.2f} (Hochachse: {'XYZ'[up]}, Hoehe {H:.2f})")
    print(f"  Oberseiten-Heightmap ({occ.sum():,} belegte Zellen von {GRID*GRID:,}):")
    print(f"    max Hoehe:            {zmax:.2f}")
    print(f"    Median / P90 / P99:   {pct(50):.2f} / {pct(90):.2f} / {pct(99):.2f}")
    print(f"    Flaeche im obersten 0.2-Band: {frac_within(0.2):5.1f} %")
    print(f"    Flaeche im obersten 0.5-Band: {frac_within(0.5):5.1f} %")
    print(f"    Flaeche im obersten 1.0-Band: {frac_within(1.0):5.1f} %")
    print(f"    Streuung der Hochpunkte ueber die Flaeche: {spread:.0f} % (hoch = verteilt, niedrig = ein Buckel)")
    return zmax, H, dims


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(os.path.dirname(__file__), "*.stl")))
    results = {}
    for p in files:
        results[os.path.basename(p)] = analyze(p)
    if len(results) > 1:
        print("\n=== Vergleich Gesamthoehen (Set-Konsistenz) ===")
        for name, (zmax, H, dims) in results.items():
            print(f"  {name:24s} Hoehe {H:6.2f}   Grundflaeche {dims[0]:.1f} x {dims[1]:.1f}")
