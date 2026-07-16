# Adaptive Relief-Optimierung fuer Untersetzer-STLs (Base/Detail-Zerlegung + lokale
# Detail-Normalisierung, Bas-Relief-Prinzip) mit HEIGHTFIELD-NEUAUFBAU.
#
# Grundsatz (mit Nutzer abgestimmt): Nur die Draufsicht zaehlt. Ueberhaenge sind
# Meshy-Artefakte; alles unter der sichtbaren Oberflaeche wird verworfen. Das
# Ergebnis-Mesh wird komplett neu aus dem transformierten Hoehenfeld aufgebaut:
# Oberflaeche (Gitter-Trianguierung) + senkrechte Aussenwand + planer Boden bei z=0.
# Dadurch: wasserdichte, saubere Topologie, keine Ueberhaenge, keine gestreckten
# Wand-Slivers, ebener Boden.
#
# Pipeline pro STL:
#   1. Dichte Oberflaechen-Samples (Vertices + Kantenmittel + flaechenproportionale
#      Zufallspunkte) -> Max-Heightmap = sichtbare Oberseite.
#   2. Felder auf 512^2: Hintergrund bg, Stuetz-Basis B (rundes Opening gross +
#      Closing klein), Plateau-Remap fB (Smoothstep-Saettigung, robuste P95-Referenz),
#      stetige Rand-Anhebung, Detail-Skalenfeld S (Auto-Gain auf --d-ceil,
#      Ornamente auf dem Untergrund behalten ihre Hoehe), optional Bilddetail.
#   3. Transformation des hochaufgeloesten Hoehenfelds (--grid, Default 1024):
#        H >= B: H' = fBeff + (H - B) * S ; darunter weicher Uebergang; z-Clamp.
#   4. Neuaufbau des Meshes aus H'.
#
# Kontrolle: _side_view.py (Seitenansichten, Querschnitte, Schraegsichten).
#
# Aufruf:
#   python _relief_opt.py                        # alle *_cut2.stl, sucht <gott>.png daneben
#   python _relief_opt.py slaanesh_cut2.stl --mode inset --d-ceil 0.5 --rim-mm 4.5
# Ausgabe: <name>_opt.stl bzw. <name>_opt-inset.stl + *_preview.png (vorher|nachher)
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

G = 512  # Feld-Aufloesung (Basis/Plateau/Skalen; Ausgabe-Aufloesung siehe --grid)


def sample_surface(tris, up, axes, cell_mm, rng):
    """Dichte Punktwolke der Oberflaeche: Ecken, Kantenmittel, Zentroide plus
    flaechenproportionale Zufallssamples (grosse flache Dreiecke abdecken)."""
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    base = [v0, v1, v2, (v0 + v1) / 2, (v1 + v2) / 2, (v2 + v0) / 2, (v0 + v1 + v2) / 3]
    e1, e2 = v1 - v0, v2 - v0
    a2 = 0.5 * np.abs(e1[:, axes[0]] * e2[:, axes[1]] - e1[:, axes[1]] * e2[:, axes[0]])
    k = np.minimum((a2 / (cell_mm * cell_mm) * 3.0).astype(int), 4096)
    idx = np.repeat(np.arange(len(tris)), k)
    if idx.size:
        r1, r2 = rng.random(idx.size), rng.random(idx.size)
        flip = r1 + r2 > 1
        r1[flip], r2[flip] = 1 - r1[flip], 1 - r2[flip]
        base.append(v0[idx] + e1[idx] * r1[:, None] + e2[idx] * r2[:, None])
    return np.concatenate(base)


def heightfield(points, up, axes, mn, dims, Gres):
    """Max-z-Heightmap [x,y] aus Punktwolke, Occupancy + Footprint; Luecken per
    Naechster-Nachbar fortgesetzt."""
    z = points[:, up] - mn[up]
    ix = np.clip(((points[:, axes[0]] - mn[axes[0]]) / dims[axes[0]] * (Gres - 1)).astype(int), 0, Gres - 1)
    iy = np.clip(((points[:, axes[1]] - mn[axes[1]]) / dims[axes[1]] * (Gres - 1)).astype(int), 0, Gres - 1)
    hm = np.full(Gres * Gres, -np.inf, dtype=np.float64)
    np.maximum.at(hm, ix * Gres + iy, z)
    hm = hm.reshape(Gres, Gres)
    occ = np.isfinite(hm)
    fp = ndimage.binary_fill_holes(ndimage.binary_closing(occ, np.ones((5, 5))))
    _, idx = ndimage.distance_transform_edt(~occ, return_indices=True)
    return hm[idx[0], idx[1]], occ, fp


def _disk(r):
    r = max(1, int(round(r)))
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return (x * x + y * y) <= r * r


def support_base(H, r_big_px, r_small_px):
    """Stuetz-Basis: Opening mit grossem RUNDEM Fenster entfernt alles Schmale ->
    Basis folgt dem Untergrund; nur breite Strukturen bleiben. Kleines Closing
    fuellt schmale Gravur-Taeler. Auf halber Aufloesung gerechnet (Tempo)."""
    H2 = H[::2, ::2]
    fo, fc = _disk(r_big_px / 2), _disk(r_small_px / 2)
    B2 = ndimage.grey_dilation(ndimage.grey_erosion(H2, footprint=fo, mode="nearest"),
                               footprint=fo, mode="nearest")
    B2 = ndimage.grey_erosion(ndimage.grey_dilation(B2, footprint=fc, mode="nearest"),
                              footprint=fc, mode="nearest")
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
    grid = np.zeros(fp.shape)
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


def rebuild_mesh(Hn, fp, mn, dims, up, axes, Gres):
    """Wasserdichtes Mesh aus dem Hoehenfeld: Oberflaeche + senkrechte Aussenwand +
    Boden (Faecher vom Zentrum; Footprint ist sternfoermig/scheibenfoermig)."""
    ax0 = mn[axes[0]] + np.arange(Gres) * dims[axes[0]] / (Gres - 1)
    ax1 = mn[axes[1]] + np.arange(Gres) * dims[axes[1]] / (Gres - 1)
    z0 = mn[up]

    def node(i, j, top=True):
        p = np.empty((len(i), 3))
        p[:, axes[0]] = ax0[i]
        p[:, axes[1]] = ax1[j]
        p[:, up] = z0 + (Hn[i, j] if top else 0.0)
        return p

    cell = fp[:-1, :-1] & fp[1:, :-1] & fp[:-1, 1:] & fp[1:, 1:]
    ci, cj = np.nonzero(cell)
    A, Bq = node(ci, cj), node(ci + 1, cj)
    C, D = node(ci + 1, cj + 1), node(ci, cj + 1)
    parts = [np.stack([A, Bq, C], 1), np.stack([A, C, D], 1)]

    # Zentrum fuer den Boden-Faecher
    fi, fj = np.nonzero(fp)
    c_b = np.zeros((1, 3))
    c_b[0, axes[0]] = ax0[fi].mean()
    c_b[0, axes[1]] = ax1[fj].mean()
    c_b[0, up] = z0

    pad = np.zeros((Gres - 1, 1), dtype=bool)
    sides = [  # (Randbedingung, Kante p->q, Aussenrichtung)
        (cell & ~np.hstack([pad, cell[:, :-1]]), lambda i, j: (i, j, i + 1, j), axes[1], -1),
        (cell & ~np.hstack([cell[:, 1:], pad]), lambda i, j: (i, j + 1, i + 1, j + 1), axes[1], +1),
        (cell & ~np.vstack([pad.T, cell[:-1, :]]), lambda i, j: (i, j, i, j + 1), axes[0], -1),
        (cell & ~np.vstack([cell[1:, :], pad.T]), lambda i, j: (i + 1, j, i + 1, j + 1), axes[0], +1),
    ]
    for mask, edge, out_ax, out_sign in sides:
        ei, ej = np.nonzero(mask)
        if not len(ei):
            continue
        pi, pj, qi, qj = edge(ei, ej)
        Pt, Qt = node(pi, pj), node(qi, qj)
        Pb, Qb = node(pi, pj, top=False), node(qi, qj, top=False)
        w1 = np.stack([Pt, Qt, Qb], 1)
        w2 = np.stack([Pt, Qb, Pb], 1)
        n = np.cross(w1[0, 1] - w1[0, 0], w1[0, 2] - w1[0, 0])
        if n[out_ax] * out_sign < 0:  # Gruppenweise nach aussen orientieren
            w1, w2 = w1[:, ::-1], w2[:, ::-1]
        cb = np.repeat(c_b, len(ei), axis=0)
        fan = np.stack([cb, Pb, Qb], 1)
        n = np.cross(fan[0, 1] - fan[0, 0], fan[0, 2] - fan[0, 0])
        if n[up] > 0:  # Boden zeigt nach unten
            fan = fan[:, ::-1]
        parts += [w1, w2, fan]

    return np.concatenate(parts).astype(np.float32)


def process(path, args):
    name = os.path.basename(path)
    verts = read_binary_stl(path).astype(np.float64)
    mn, mx = verts.min(axis=0), verts.max(axis=0)
    dims = mx - mn
    up = int(np.argmin(dims))
    axes = [a for a in range(3) if a != up]
    px_per_mm = (G - 1) / float(max(dims[axes[0]], dims[axes[1]]))
    Ghi = args.grid
    cell_hi_mm = float(max(dims[axes[0]], dims[axes[1]])) / (Ghi - 1)

    rng = np.random.default_rng(12345)
    pts = sample_surface(verts.reshape(-1, 3, 3), up, axes, cell_hi_mm, rng)
    H, occ, fp = heightfield(pts, up, axes, mn, dims, G)
    zmax = float(H[fp].max())

    # Hintergrund-Niveau: Modalwert der unteren Haelfte (0.25-mm-Bins)
    vals = H[fp]
    lower = vals[vals <= np.median(vals)]
    hist, edges = np.histogram(lower, bins=max(8, int(np.ptp(lower) / 0.25)))
    bg = args.bg if args.bg is not None else float((edges[np.argmax(hist)] + edges[np.argmax(hist) + 1]) / 2)

    # 2. Basis: Stuetzflaeche + Glaettung
    B = support_base(H, args.r_detail * px_per_mm, args.r_small * px_per_mm)
    B = ndimage.gaussian_filter(B, args.smooth_mm * px_per_mm)
    D = H - B  # nur fuer Envelope/Statistik

    # 3. Basis-Remap: ab --sat der (robusten) Basishoehe exakt Plateau P
    raised = B[fp][B[fp] > bg + 0.5]
    B_hi = float(np.percentile(raised, 95)) if raised.size else float(B[fp].max())
    P = args.plateau_mm if args.plateau_mm is not None else bg + args.plateau * (zmax - bg)
    t = (B - bg) / max(B_hi - bg, 1e-9)
    fB = bg + (P - bg) * smoothstep(t / args.sat)
    fB = np.where(B < bg, B, fB)  # unterhalb bg Identitaet
    if args.rim_mm > 0:
        # Aussenrand stetig aufs Plateau blenden (kein Gate, kein Veto: an der
        # Aussenkante faellt B unter bg, ein harter Schwellwert riss den Ring auf)
        dist_in = ndimage.distance_transform_edt(fp) / px_per_mm  # mm vom Aussenrand
        w_rim = smoothstep((args.rim_mm + 2.0 - dist_in) / 2.0)
        fB = fB + (P - fB) * w_rim  # reines Lerp: innen (w=0) unveraendert, am Rand exakt P

    # 4. Detail-Skalenfeld S
    dC = args.d_ceil
    env_px = max(3, int(round(args.r_detail * px_per_mm)) | 1)
    Dpos = np.minimum(np.maximum(D, 0), 3.0 * dC)  # Amplitude kappen (harte Dilations-Schatten)
    Dloc = ndimage.gaussian_filter(ndimage.grey_dilation(Dpos, size=(env_px, env_px)), env_px / 2.5)
    Dloc = np.maximum(Dloc, ndimage.gaussian_filter(Dpos, 1.5))
    S_pl = dC / np.maximum(Dloc, dC / 2.0)
    S_pl = 1.0 + (S_pl - 1.0) * np.where(S_pl > 1.0, smoothstep(Dloc / (0.5 * dC)), 1.0)
    cap_bg = args.cap_bg * (P - bg)
    S_bg = np.minimum(1.0, cap_bg / np.maximum(Dloc, 1e-6))
    w_pl = np.clip((fB - bg) / max(P - bg, 1e-9), 0, 1)
    S = S_bg + (S_pl - S_bg) * w_pl
    S = np.minimum(S, (P + dC - fB) / np.maximum(Dloc, 1e-6))  # Deckel: nie ueber P + d_ceil
    S = np.maximum(S, 0.0)
    S = ndimage.gaussian_filter(S, 1.5)

    # 5. effektives Plateau-Feld (inset-Senkung, optionales Bilddetail)
    FBe = fB.copy()
    if args.mode == "inset":
        FBe -= np.clip(Dloc * S, 0, dC) * w_pl

    img_note = "kein Bild"
    png = args.png or re.sub(r"_cut\d*(_soft)?\.stl$", ".png", path)
    if os.path.exists(png):
        grid_img = load_image_grid(png, fp)
        grid_img, corr, flip = best_flip(grid_img, H, fp)
        img_note = f"{os.path.basename(png)} ({flip}, Kanten-r={corr:.2f})"
        if args.img_detail > 0:
            if corr < 0.15:
                print(f"  WARNUNG: Bildkorrelation nur {corr:.2f} - --img-detail wird uebersprungen")
            else:
                Dimg = grid_img - ndimage.gaussian_filter(grid_img, args.img_sigma_mm * px_per_mm)
                Dimg /= max(np.percentile(np.abs(Dimg[fp]), 95), 1e-9)
                w_gap = 1.0 - np.clip(Dloc / dC, 0, 1)
                FBe += args.img_detail * np.clip(Dimg, -1.5, 1.5) * w_pl * w_gap

    # 6. Hochaufgeloestes Hoehenfeld transformieren und Mesh neu aufbauen
    Hhi, occhi, fphi = heightfield(pts, up, axes, mn, dims, Ghi)
    sc = (G - 1) / (Ghi - 1)
    gi = np.arange(Ghi) * sc
    cx, cy = np.meshgrid(gi, gi, indexing="ij")
    samp = lambda F: ndimage.map_coordinates(F, [cx, cy], order=1, mode="nearest")
    bv, fv, sv = samp(B), samp(FBe), samp(S)
    zA = 0.35 * bg
    t_low = (Hhi - zA) / np.maximum(bv - zA, 1e-6)
    Hn = np.where(Hhi >= bv, fv + (Hhi - bv) * sv, Hhi + (fv - bv) * smoothstep(t_low))
    knee = P + (dC if args.mode == "raise" else 0.0) + 0.05
    span = 0.2
    Hn = np.where(Hn > knee, knee + span * np.tanh((Hn - knee) / span), Hn)
    Hn = np.maximum(Hn, 0.2)  # Oberflaeche bleibt ueber dem Boden

    tris_out = rebuild_mesh(Hn, fphi, mn, dims, up, axes, Ghi)
    suffix = "_opt.stl" if args.mode == "raise" else "_opt-inset.stl"
    out_path = os.path.splitext(path)[0].replace("_cut2", "") + suffix
    write_binary_stl(out_path, tris_out,
                     f"relief-opt rebuild bg={bg:.2f} P={P:.2f} dC={dC} {args.mode}")

    # Statistik + Vorschau (halbe Aufloesung reicht)
    _, before = band_fracs(Hhi[occhi])
    zref_n, after = band_fracs(Hn[occhi])
    pv = np.concatenate([shade(Hhi[::2, ::2], fphi[::2, ::2], px_per_mm),
                         shade(Hn[::2, ::2], fphi[::2, ::2], px_per_mm)], axis=1)
    pv_path = os.path.splitext(out_path)[0] + "_preview.png"
    Image.fromarray(pv).save(pv_path)

    print(f"\n=== {name} -> {os.path.basename(out_path)} ===")
    print(f"  Hintergrund {bg:.2f} / Plateau {P:.2f} / r-detail {args.r_detail} mm / d-ceil {dC} mm / Bild: {img_note}")
    print(f"  Neuaufbau: {len(tris_out):,} Dreiecke aus {Ghi}x{Ghi}-Hoehenfeld, Boden plan bei 0")
    print(f"  Hoehe (max): {zmax:.2f} -> {float(Hn[fphi].max()):.2f}; Referenz P99.8: {zref_n:.2f}")
    print(f"  Flaeche im Band unter Referenz (vorher -> nachher):")
    for d in (0.2, 0.5, 1.0):
        print(f"    {d:.1f}-Band: {before[d]:5.1f} % -> {after[d]:5.1f} %")
    print(f"  Vorschau: {os.path.basename(pv_path)} (links vorher, rechts nachher)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Adaptive Relief-Optimierung mit Heightfield-Neuaufbau.")
    ap.add_argument("files", nargs="*", help="STL-Dateien (Default: alle *_cut2.stl im Skriptordner)")
    ap.add_argument("--grid", type=int, default=1024, help="Aufloesung des Neuaufbau-Hoehenfelds (Default 1024)")
    ap.add_argument("--r-detail", type=float, default=5.0, help="Detail-Radius in mm: Schmaleres als ~2r ist Detail (Default 5)")
    ap.add_argument("--r-small", type=float, default=3.0, help="Closing-Radius in mm: Gravuren bis ~2r bleiben Detail (Default 3)")
    ap.add_argument("--rim-mm", type=float, default=6.0, help="Aussenrand-Zone in mm, die aufs Plateau gezogen wird (0 = aus, Default 6)")
    ap.add_argument("--cap-bg", type=float, default=0.75, help="Max. Ornamenthoehe auf dem Untergrund als Anteil von (P-bg) (Default 0.75)")
    ap.add_argument("--smooth-mm", type=float, default=1.2, help="Glaettung der Basis in mm (Default 1.2)")
    ap.add_argument("--plateau", type=float, default=0.5, help="Plateau als Anteil der Reliefhoehe ueber Hintergrund (Default 0.5)")
    ap.add_argument("--plateau-mm", type=float, help="Plateau absolut in mm (ueberschreibt --plateau)")
    ap.add_argument("--sat", type=float, default=0.5, help="Basis-Anteil, ab dem exakt Plateauhoehe erreicht wird (Default 0.5)")
    ap.add_argument("--bg", type=float, help="Hintergrund-Niveau in mm (Default: automatisch)")
    ap.add_argument("--d-ceil", type=float, default=0.8, help="Ziel-Detailamplitude ueber dem Plateau in mm (Default 0.8)")
    ap.add_argument("--mode", choices=["raise", "inset"], default="raise",
                    help="raise: Detail steht ueber dem Plateau. inset: Detail ins Plateau eingelassen (maximale Auflageflaeche)")
    ap.add_argument("--img-detail", type=float, default=0.0, help="Detail aus PNG-Vorlage in mm Amplitude einpraegen (Default 0 = aus)")
    ap.add_argument("--img-sigma-mm", type=float, default=1.5, help="Highpass-Radius fuer Bilddetail in mm (Default 1.5)")
    ap.add_argument("--png", help="Pfad zur Bildvorlage (Default: <gott>.png neben der STL)")
    args = ap.parse_args()
    files = args.files or sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "*_cut2.stl")))
    if not files:
        raise SystemExit("keine STL-Dateien gefunden")
    for p in files:
        process(p, args)
