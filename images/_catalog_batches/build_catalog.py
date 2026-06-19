"""Baut images/image_catalog.md aus den gesammelten Roh-Bloecken.

- parst @@@-Bloecke (FILE/CAT/TYPE/DESC)
- gruppiert nach Kategorie
- dedupliziert nach Dateiname
- validiert gegen die tatsaechlich vorhandenen Bilddateien
- meldet Bilder ohne Katalogeintrag und Eintraege ohne Datei
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.dirname(HERE)            # ...\images
RAW = os.path.join(HERE, "raw_blocks.txt")
OUT = os.path.join(IMG_DIR, "image_catalog.md")

CATS = {
    1: "1 · Adeptus Custodes",
    2: "2 · Adeptus Astartes (Space Marines / Primaris)",
    3: "3 · Adepta Sororitas & Sisters of Silence",
    4: "4 · Astra Militarum (Garde, Tempestus, Kommissare, Ogryn)",
    5: "5 · Adeptus Mechanicus & Tech (Tech-Priester, Skitarii, Servitoren)",
    6: "6 · Navigatoren / Astropathen / Psioniker",
    7: "7 · Ecclesiarchy / Klerus / Prediger",
    8: "8 · Adel, Verwaltung, Rogue Trader, Zivilisten, Schiffscrew",
    9: "9 · Arbites & Assassinen",
    10: "10 · Aeldari (Craftworld, Corsairs, Rangers, Farseer)",
    11: "11 · Harlequins",
    12: "12 · Drukhari (Dark Eldar)",
    13: "13 · Necrons",
    14: "14 · Chaos / Death Guard / Nurgle / Kultisten / Dämonen",
    15: "15 · Orte, Schiffe, Landschaften, Architektur",
    16: "16 · Sonstiges / nicht eindeutig",
}

IMG_EXTS = (".png", ".jpg", ".jpeg")


def parse_blocks(text):
    blocks = []
    for chunk in text.split("@@@"):
        chunk = chunk.strip()
        if not chunk:
            continue
        rec = {}
        cur = None
        for line in chunk.splitlines():
            m = re.match(r"^(FILE|CAT|TYPE|DESC):\s?(.*)$", line)
            if m:
                cur = m.group(1)
                rec[cur] = m.group(2).strip()
            elif cur == "DESC":
                rec["DESC"] += " " + line.strip()
        if "FILE" in rec and "CAT" in rec:
            try:
                rec["CAT"] = int(re.sub(r"\D", "", rec["CAT"]) or "16")
            except ValueError:
                rec["CAT"] = 16
            rec.setdefault("TYPE", "?")
            rec.setdefault("DESC", "")
            blocks.append(rec)
    return blocks


def main():
    with open(RAW, encoding="utf-8") as f:
        blocks = parse_blocks(f.read())

    # dedupe nach FILE (erster gewinnt)
    seen = {}
    for b in blocks:
        seen.setdefault(b["FILE"], b)

    disk = {fn for fn in os.listdir(IMG_DIR)
            if fn.lower().endswith(IMG_EXTS)}

    cataloged = set(seen)
    missing_on_disk = sorted(cataloged - disk)      # Eintrag ohne Datei (Tippfehler)
    not_cataloged = sorted(disk - cataloged)        # Datei ohne Eintrag

    # gruppieren
    by_cat = {}
    for b in seen.values():
        if b["FILE"] in disk:
            by_cat.setdefault(b["CAT"], []).append(b)
    for c in by_cat:
        by_cat[c].sort(key=lambda r: r["FILE"].lower())

    total = sum(len(v) for v in by_cat.values())

    lines = []
    lines.append("# Bild-Katalog – Gilead-Kampagne")
    lines.append("")
    lines.append(f"Automatisch erzeugter Katalog aller {total} Bilder im `images/`-Ordner, "
                 "thematisch gruppiert. **So arbeitest du damit:** Trage hinter "
                 "**Name/Ort:** den gewünschten Namen ein (Person oder Ort). Wenn du fertig bist, "
                 "kann ich die Bilddateien anhand der vergebenen Namen umbenennen.")
    lines.append("")
    lines.append("> Neu generieren: `python images/_catalog_batches/build_catalog.py`")
    lines.append("")
    # Inhaltsverzeichnis
    lines.append("## Inhalt")
    for c in sorted(by_cat):
        anchor = re.sub(r"[^a-z0-9 -]", "", CATS[c].lower()).replace(" ", "-")
        lines.append(f"- [{CATS[c]}](#{anchor}) — {len(by_cat[c])}")
    lines.append("")

    for c in sorted(by_cat):
        lines.append(f"## {CATS[c]}")
        lines.append("")
        for b in by_cat[c]:
            fn = b["FILE"]
            lines.append(f"#### `Name/Ort: ____________________`")
            lines.append(f"![](<{fn}>)")
            lines.append("")
            lines.append(f"*{b['TYPE']}* — {b['DESC']}")
            lines.append("")
            lines.append(f"<sub>`{fn}`</sub>")
            lines.append("")
            lines.append("---")
            lines.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Katalog geschrieben: {OUT}")
    print(f"Eintraege im Katalog: {len(cataloged)} | Bilder auf Platte: {len(disk)} | im Katalog gelistet: {total}")
    if missing_on_disk:
        print(f"\nEintraege OHNE passende Datei ({len(missing_on_disk)}):")
        for x in missing_on_disk:
            print("  -", x)
    if not_cataloged:
        print(f"\nBilder OHNE Katalogeintrag ({len(not_cataloged)}):")
        for x in not_cataloged:
            print("  -", x)
    if not missing_on_disk and not not_cataloged:
        print("\nAlles konsistent: jede Datei hat genau einen Eintrag.")


if __name__ == "__main__":
    main()
