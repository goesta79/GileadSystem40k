# Seitenansichten + Querschnitte einer binaeren STL als PNG rendern (Selbstkontrolle).
# Orthografische Projektion per Punktwolke (Vertices + Kantenmittelpunkte + Zentroide),
# tiefen-schattiert; dazu duenne Querschnitts-Schnitte durch die Mitte.
#
# Aufruf:
#   python _side_view.py datei.stl [weitere.stl ...] [--ppm 8] [--zx 1.0]
# Ausgabe: <name>_side.png mit 4 Streifen:
#   1) Ansicht von vorn (Blick entlang -Y)   2) Querschnitt Y-Mitte (Dicke ~1 mm)
#   3) Ansicht von rechts (Blick entlang -X) 4) Querschnitt X-Mitte
import argparse
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _analyze_z import read_binary_stl


def densify(tris):
    """Punktwolke: Ecken + Kantenmittel + Zentroide (fuer grob tesselierte Flaechen)."""
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    return np.concatenate([
        v0, v1, v2,
        (v0 + v1) / 2, (v1 + v2) / 2, (v2 + v0) / 2,
        (v0 + v1 + v2) / 3,
    ])


def render_view(pts, ax_u, ax_z, ax_d, ppm, zx, section=None):
    """Orthografische Ansicht: ax_u = Bild-x, ax_z = Hoehe, ax_d = Tiefe (Kamera bei -ax_d).
    section=(mitte, dicke): nur Punkte im Schnittband rendern (weiss)."""
    u, z, d = pts[:, ax_u], pts[:, ax_z], pts[:, ax_d]
    if section is not None:
        m = np.abs(d - section[0]) <= section[1]
        u, z, d = u[m], z[m], d[m]
    umin, zmin = u.min(), z.min()
    W = int(np.ceil((u.max() - umin) * ppm)) + 3
    Hpx = int(np.ceil((z.max() - zmin) * ppm * zx)) + 3
    px = np.clip(((u - umin) * ppm).astype(int) + 1, 0, W - 1)
    py = np.clip(Hpx - 2 - ((z - zmin) * ppm * zx).astype(int), 0, Hpx - 1)
    img = np.zeros((Hpx, W), dtype=np.float32)
    if section is not None:
        img[py, px] = 255.0
    else:
        depth = np.full(Hpx * W, np.inf, dtype=np.float64)
        np.minimum.at(depth, py * W + px, d)
        hit = np.isfinite(depth)
        dn = depth[hit]
        lo, hi = np.percentile(dn, 2), np.percentile(dn, 98)
        shadev = 220 - 150 * np.clip((dn - lo) / max(hi - lo, 1e-9), 0, 1)
        buf = np.zeros(Hpx * W, dtype=np.float32)
        buf[hit] = shadev
        img = buf.reshape(Hpx, W)
    return img.astype(np.uint8)


def stack(strips, gap=8):
    W = max(s.shape[1] for s in strips)
    total = sum(s.shape[0] for s in strips) + gap * (len(strips) - 1)
    out = np.full((total, W), 30, dtype=np.uint8)
    yy = 0
    for s in strips:
        out[yy:yy + s.shape[0], :s.shape[1]] = s
        yy += s.shape[0] + gap
    return out


def process(path, ppm, zx):
    verts = read_binary_stl(path).astype(np.float64)
    tris = verts.reshape(-1, 3, 3)
    pts = densify(tris)
    dims = pts.max(axis=0) - pts.min(axis=0)
    up = int(np.argmin(dims))
    a, b = [ax for ax in range(3) if ax != up]
    mid_b = (pts[:, b].max() + pts[:, b].min()) / 2
    mid_a = (pts[:, a].max() + pts[:, a].min()) / 2
    strips = [
        render_view(pts, a, up, b, ppm, zx),
        render_view(pts, a, up, b, ppm, zx, section=(mid_b, 0.6)),
        render_view(pts, b, up, a, ppm, zx),
        render_view(pts, b, up, a, ppm, zx, section=(mid_a, 0.6)),
    ]
    out_path = os.path.splitext(path)[0] + "_side.png"
    Image.fromarray(stack(strips)).save(out_path)
    print(f"{os.path.basename(path)}: {os.path.basename(out_path)} "
          f"(BBox {dims[a]:.1f} x {dims[b]:.1f} x {dims[up]:.2f}, Ansicht+Schnitt je Achse)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Orthografische Seitenansichten/Querschnitte einer STL als PNG.")
    ap.add_argument("files", nargs="+", help="STL-Dateien")
    ap.add_argument("--ppm", type=float, default=8.0, help="Pixel pro mm horizontal (Default 8)")
    ap.add_argument("--zx", type=float, default=1.0, help="Z-Ueberhoehung (Default 1.0 = massstabsgetreu)")
    args = ap.parse_args()
    for p in args.files:
        process(p, args.ppm, args.zx)
