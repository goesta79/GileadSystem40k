    # Index – Gilead Kampagne (Wrath & Glory 2e)

Dieser Index trackt die Ordnerstruktur und Inhalte des Workspace.

## Wurzelverzeichnis
- `CLAUDE.md` – Projektregeln & Prämisse für die KI-Unterstützung
- `README.md` – Projektbeschreibung
- `index.md` – dieser Index
- `index.html`, `Gilead-map.html`, `npc-tracker.html` – Web-Tools (NPC-Tracker, Systemkarte)
- `foo.py` – Hilfsskript

## campaign/
Kreativ-Inhalte und Knowledge-Base der Kampagne. Word-Originale (`.docx`) und konvertierte Markdown-Fassungen (`.md`).

- `Ages of the Empire` – Zeitalter/Hintergrund des Imperiums
- `DIE VERKÜNDUNG DER ZWEI PFADE` – Prophezeiungstext
- `Die Varonius Flottille` – Hintergrund Freihändler-Flottille
- `Dispensatus Anathema` – Dokument/Edikt
- `Hüterin Prophezeiung` – Prophezeiung der Hüterin
- `NPC-Dossier_Gilead_Kampagne` – NPC-Übersicht
- `Planetare und zivile Führung` – Führungsfiguren des Systems
- `SPOILER - NPC Dossiers` – ausführliche NPC-Dossiers (Spoiler)
- `SPOILER Prophezeiung der zwei Pfade` – Spoiler-Prophezeiung
- `SPOILER die große Expedition` – Spoiler Expeditions-Plot
- `SPOILER_ Plotbuch` – Spoiler Plotübersicht
- `SPOILER_ Prophezeiung der Hüterin` – Spoiler-Prophezeiung
- `VORSICHT SPOILER - Npc Portraits` – NPC-Portraits (Spoiler)
- `Zähne aus Silber messerscharf` – Vers/Gedicht (Myravels Töchter)
- `characters` – Spielercharaktere (Tier 3)
- `past_adventures` – Chronik Abenteuer 1–4
- `Der Miravel Clan` – Dossier des gemäßigten Drukhari-Clans (Myravel)
- `Abenteuer 5 - Weggabelung` – Planung Abenteuer 5 (Zwei-Pfade-Entscheidung)
- `Abenteuer 5 - Pfad-Eröffnungen` – Szenen-Gerüst beider Pfade (A: Webway/Drukhari, B: Necron-Gruft)
- `Abenteuer 5 - Fluff (Basar & Necron-Ankunft)` – 10 Basar-Vignetten + 3 Eröffnungstexte Necron-Gruft
- `_convert_docx.py` – Skript zur Konvertierung der `.docx` nach Markdown

## lore/
Aus dem [Lexicanum](https://wh40k.lexicanum.com) gescrapte Hintergrundartikel als Markdown (CC BY-SA, private Nutzung). Jede Datei verlinkt im Kopf ihre Quelle. **101 Artikel** (Lauf 1), gewichtet nach den im `campaign/`-Ordner vorkommenden Stichwörtern.

Werkzeuge:
- `_scrape_lexicanum.py` – Scraper (`python lore/_scrape_lexicanum.py articles.txt` oder `... "Artikel" ...`)
- `articles.txt` – kuratierte Titelliste für Lauf 1 (Top 100 Grundlagen)
- `articles_run2.txt` – Lauf 2: Fokus Webway, Necron-Gruftwelten (Tomb World, Dolmen Gate), Drukhari-Enklaven (Haemonculi, Wych Cult, Kabal), Webway-Realms (Exodite, Crone World). Hinweis: eine eigenständige Eldar-„Black Library" gibt es auf Lexicanum nicht (im `Webway`-Artikel mitbehandelt).

Inhaltliche Schwerpunkte (Auswahl): Imperium-Grundlagen (Imperium, Emperor of Mankind, High Lords, Great Crusade, Horus Heresy), Adeptus Astartes & Primarchen, Chaos & Chaosgötter, der Warp, Astra Militarum, Adeptus Mechanicus & Titanen, Adeptus Custodes & Sisters of Silence, Adepta Sororitas & Ecclesiarchy, Inquisition (inkl. Ordos & Grey Knights), Assassinorum, Astropathen/Psyker/Navigatoren, Arbites/Administratum/Munitorum, Rogue Trader, Necrons (inkl. C'tan), Aeldari & Drukhari, T'au, Orks, Tyraniden/Genestealer, Weltentypen sowie das kanonische **Gilead System** (W&G-Setting, nennt u.a. die Absolvers, Ul-Khari, Ostia, Primus).

## PDF/
Regelwerke, Quellenbücher und Abenteuer für Wrath & Glory (Corebook v2.1/v3, Errata, Abenteuermodule, Threat Assessments, Charakterbögen u.a.).

## images/
Bild- und Referenzmaterial (KI-generierte Porträts, Orte, Szenen). **317 Bilder.**
- `image_catalog.md` – thematisch gruppierter Katalog aller Bilder (16 Kategorien) mit Beschreibung und Namens-Platzhalter pro Bild. Workflow: Platzhalter ausfüllen → Bilder können später entsprechend umbenannt werden.
- `_catalog_batches/` – Generator-Werkzeuge: `build_catalog.py` (baut den Katalog), `raw_blocks.txt` (Rohbeschreibungen). Neu bauen: `python images/_catalog_batches/build_catalog.py`.

## other_media/
Weiteres Medienmaterial.
