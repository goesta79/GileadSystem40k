"""Holt einzelne Lexicanum-Wiki-Artikel und legt sie als Markdown in lore/ ab.

Aufruf:
    python lore/_scrape_lexicanum.py "Adeptus Custodes" "Imperium" ...

Hinweis: Inhalte stammen von wh40k.lexicanum.com (CC BY-SA, basierend auf
Games-Workshop-Material) und dienen ausschließlich der privaten
Kampagnen-Vorbereitung. Quelle wird im Kopf jeder Datei verlinkt.
"""
import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE = "https://wh40k.lexicanum.com/wiki/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
HERE = os.path.dirname(os.path.abspath(__file__))


def slug_to_filename(title):
    safe = re.sub(r'[<>:"/\\|?*]', "_", title).strip()
    return safe + ".md"


def fetch(title):
    url = BASE + title.replace(" ", "_")
    r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    return url, r.text


def extract(html):
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.select_one("#firstHeading")
    title = heading.get_text(strip=True) if heading else ""
    content = soup.select_one("#mw-content-text")
    if content is None:
        raise RuntimeError("Kein Hauptinhalt (#mw-content-text) gefunden")

    # Aufräumen: Navigation, Bearbeiten-Links, Bildboxen, Fußnoten etc.
    drop_selectors = [
        ".toc", ".mw-editsection", ".thumb", ".gallery", ".navbox",
        ".metadata", ".noprint", "table.infobox", ".reference",
        "#toc", ".printfooter", ".catlinks", "style", "script",
        "sup.reference", ".mw-empty-elt",
    ]
    for sel in drop_selectors:
        for el in content.select(sel):
            el.decompose()

    for el in content.select("div.hatnote, .dablink, .ambox"):
        el.decompose()

    body = md(str(content), heading_style="ATX", strip=["a"])

    # Zitations-Marker wie [1], [25w], [76a], [Notes] entfernen
    body = re.sub(r"\[(\d+[a-z]*|Notes)\]", "", body)
    # Bild-Einbindungen entfernen
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    # Tabellenzeilen mit Bilddateinamen oder "redirects here" entfernen
    cleaned = []
    for line in body.splitlines():
        if re.search(r"\.(gif|png|jpg|jpeg|svg)\b", line, re.IGNORECASE):
            continue
        if "redirects here" in line.lower():
            continue
        cleaned.append(line)
    body = "\n".join(cleaned)

    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    # alles ab Überschrift Sources/References/Related abtrennen
    body = re.split(r"\n#+\s*(Sources|References|Related Articles)\b",
                    body, flags=re.IGNORECASE)[0].strip()
    return title, body


def save(title, url, body):
    fname = slug_to_filename(title)
    path = os.path.join(HERE, fname)
    header = (
        f"# {title}\n\n"
        f"> Quelle: [{url}]({url}) — Lexicanum (CC BY-SA). "
        f"Auszug für private Kampagnen-Vorbereitung.\n\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + body + "\n")
    return path


def main(titles):
    for i, title in enumerate(titles):
        try:
            url, html = fetch(title)
            real_title, body = extract(html)
            path = save(real_title or title, url, body)
            print("OK", os.path.basename(path), f"({len(body)} Zeichen)")
        except Exception as e:
            print("FEHLER", title, "->", e)
        if i < len(titles) - 1:
            time.sleep(1.5)  # höflich zum Server


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Aufruf: python lore/_scrape_lexicanum.py "Artikel 1" "Artikel 2" ...')
        sys.exit(1)
    main(sys.argv[1:])
