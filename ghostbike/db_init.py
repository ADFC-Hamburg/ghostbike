import json
import os
from datetime import datetime, date
from typing import Dict, List, Type, Any, Optional
import re
import math
from ghostbike.tables import (
    Infrastructure, MainFault, AccidentCode, AccidentType, LocationType, NewspaperMedium,
    Opponent, StreetType, Ghostbike, NewspaperArticle
)
from piccolo.table import Table
from urllib.parse import urlparse

# Konfiguration für alle Default-Daten
DEFAULT_DATA_CONFIG: Dict[Type[Table], List[Dict[str, Any]]] = {
    Opponent: [
        {"key": "Bus", "name": "Bus"},
        {"key": "Fahrrad", "name": "Fahrrad"},
        {"key": "LKW", "name": "LKW"},
        {"key": "PKW", "name": "PKW"},
        {"key": "Motorrad", "name": "Motorrad"},
        {"key": "solo", "name": "Alleinunfall"},
        {"key": "sonstige", "name": "Sonstige"},
    ],
    LocationType: [
        {"key": "a", "name": "außerorts"},
        {"key": "i", "name": "innerorts"},
    ],
    Infrastructure: [
        {"key": "FB", "name": "nur Fahrbahn vorhanden"},
        {"key": "RVA", "name": "straßenbegleitende Radverkehrsanlage vorhanden"},
        {"key": "Weg", "name": "Weg ohne öffentlichen KFZ-Verkehr"},
    ],
    MainFault: [
        {"key": "r", "name": "Radfahrende"},
        {"key": "g", "name": "Kraftfahrender Gegner"},
        {"key": "s", "name": "Alleinunfall"},
        {"key": "f", "name": "Fußgänger/Haustier"},
        {"key": "o", "name": "Schuld offen"},
    ],
    StreetType: [
        {"key": "a", "name": "außerorts"},
        {"key": "i", "name": "innerorts"},
        {"key": "b", "name": "Bundesstraße"},
        {"key": "l", "name": "Landes-/Staatsstraße"},
        {"key": "k", "name": "Kreisstraße, Ortsverbindungsstraße"},
        {"key": "v", "name": "Vorfahrtstraße innerorts"},
        {"key": "n", "name": "Nebenstraße innerorts"},
        {"key": "h", "name": "Hauptstraße innerorts"},
        {"key": "w", "name": "Weg"},
    ],
    AccidentType: [
        {"key": "solo", "name": "Alleinsturz durch Fahrfehler oder Gesundheitsproblem"},
        {"key": "FQ", "name": "Fahrbahnquerung RF"},
        {"key": "VF", "name": "einer der Beteiligten begeht einen Vorfahrtfehler"},
        {"key": "andere", "name": "u.a. Fehler b. LA, Fahrunfälle, Unfälle mit anderen RF, FG oder Haustieren"},
        {"key": "RA", "name": "KFZ Rechtsabbieger über RVA"},
        {"key": "Ü", "name": "KFZ rammt oder streift RF auf FB von hinten"},
        {"key": "frontal", "name": "Frontalzusammenstoß mit KFZ auf FB im Gegenverkehr"},
        {"key": "BÜ", "name": "Bahnübergang, RF quert Schienen"},
        {"key": "Einfahren", "name": "einer der Beteiligten fährt in die Straße ein"},
        {"key": "unklar", "name": "kein eindeutiger Unfallhergang veröffentlicht"},
    ],
    AccidentCode: [
        {"code": 141, "name": "Ohne Mitwirkende Besonderheiten von Querschnitt und Längsneigung Gerade"},
        {"code": 149, "name": "Ohne Mitwirkende Besonderheiten von Querschnitt und Längsneigung"},
        {"code": 189, "name": "Straßenverlauf nicht bekannt"},
        {"code": 199, "name": "Sontiger Fahrunfall"},
        {"code": 211, "name": "Linksabbieger in gleiche Richtung"},
        {"code": 224, "name": "Linksabbieger in Gegenrichtung"},
        {"code": 241, "name": "Rechtsabbieger in gleiche Richtung gesrtreift"},
        {"code": 243, "name": "Rechtsabbieger in gleiche Richtung voll"},
        {"code": 244, "name": "Rechtsabbieger in Gegenrichtung"},
        {"code": 261, "name": "Linksabbieger Wartepflichtiger"},
        {"code": 299, "name": "Sonstiger Abbigeunfall"},
        {"code": 341, "name": "Bevorrechtiges Fahrzeug, Radweg von links"},
        {"code": 373, "name": "Radwegaufleitung von Rechts"},
        {"code": 379, "name": "Einfahrender Radfaher, Richtung unklar"},
        {"code": 399, "name": "Sonstige Einbiegeunfall"},
        {"code": 499, "name": "Sonstige Überschreiten-Unfall"},
        {"code": 599, "name": "Sontiger Ruhender Verkehr Unfall"},
        {"code": 601, "name": "Vorrausfahrender Einspurig"},
        {"code": 646, "name": "Spurwechsler nach rechts nach Überholen auf Richtungsfahrbahn"},
        {"code": 699, "name": "Sonstiger Unfall im Längsverkehr"},
        {"code": 762, "name": "Schwächeanfall"},
        {"code": 799, "name": "Sonstiger Unfall"},
    ],
    NewspaperMedium: [
        {"name": "Süderelbe24", "url": "https://suederelbe24.de"},
        {"name": "Unfallatlas", "url": "https://unfallatlas.statistikportal.de"},
        {"name": "Hamburger Abendblatt", "url": "https://www.abendblatt.de"},
        {"name": "BILD", "url": "https://www.bild.de"},
        {"name": "Hamburgische Bürgerschaft",
            "url": "https://www.buergerschaft-hh.de"},
        {"name": "Kieler Nachrichten", "url": "https://www.kn-online.de"},
        {"name": "Hamburger Morgenpost", "url": "https://www.mopo.de"},
        {"name": "Norddeutscher Rundfunk", "url": "https://www.ndr.de"},
        {"name": "Presseportal", "url": "https://www.presseportal.de"},
        {"name": "RTN TV News", "url": "https://www.rtntvnews.de"},
        {"name": "Schleswig-Holsteinische Zeitung", "url": "https://www.shz.de"},
        {"name": "DIE WELT", "url": "https://www.welt.de"},
    ]
}


# Mapping von JSON-Feldern zu Datenbank-Keys
FIELD_MAPPINGS = {
    "street_type": {
        "h": "h",  # Hauptstraße
        "n": "n",  # Nebenstraße
        "b": "b",  # Bundesstraße
        "l": "l",  # Landesstraße
        "k": "k",  # Kreisstraße
        "a": "a",  # außerorts
        "i": "i",  # innerorts
        "w": "w",  # Weg
        "v": "v",  # Vorfahrtstraße
    },
    "accident_type": {
        "RA": "RA",
        "andere": "andere",
        "solo": "solo",
        "FQ": "FQ",
        "VF": "VF",
        "frontal": "frontal",
        "BÜ": "BÜ",
        "Einfahren": "Einfahren",
        "unklar": "unklar",
        "Ü": "Ü",
    },
    "location_type": {
        "i": "i",  # innerorts
        "o": "a",  # außerorts -> außerorts
        "a": "a",  # außerorts
    },
    "opponent": {
        "LKW": "LKW",
        "PKW": "PKW",
        "Motorrad": "Motorrad",
        "solo": "solo",
        "sonstige": "sonstige",
        "Bus": "Bus",
        "Fahrrad": "Fahrrad",
    },
    "infrastructure": {
        "RVA": "RVA",
        "FB": "FB",
        "Weg": "Weg",
    },
    "main_fault": {
        "r": "r",  # Radfahrende
        "g": "g",  # Kraftfahrender Gegner
        "s": "s",  # Alleinunfall
        "f": "f",  # Fußgänger/Haustier
        "o": "o",  # Schuld offen
    }
}


async def get_medium_id_from_url(presse_url: str) -> Optional[int]:
    """Ermittelt die medium_id basierend auf dem Hostnamen der presse_url."""
    if not presse_url:
        return None

    try:
        # Hostname aus der URL extrahieren
        parsed_url = urlparse(presse_url)
        hostname = parsed_url.netloc.lower()
        print(f"Suche Medium für Hostname: {hostname}")
        # Medium anhand des Hostnames suchen
        medium = await NewspaperMedium.select().where(
            NewspaperMedium.url.ilike(f"%{hostname}%")
        ).first()
        print(medium)
        return medium['id'] if medium else None
    except Exception:
        return None


def parse_date(date_str: str) -> Optional[datetime]:
    """Parst Datum aus verschiedenen Formaten."""
    if not date_str or date_str == "NaN":
        return None

    try:
        # Format: "2013-05-09 00:00:00"
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()
    except ValueError:
        try:
            # Format: "2013-05-09"
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"Warnung: Kann Datum nicht parsen: {date_str}")
            return None


def clean_string(value: Any) -> Optional[str]:
    """Bereinigt String-Werte und behandelt NaN/None."""
    if value is None or value == "NaN" or str(value).strip() == "":
        return None
    return str(value).strip()


def clean_number(value: Any) -> Optional[float]:
    """Bereinigt Zahlen-Werte und behandelt NaN/None."""
    if value is None or value == "NaN" or str(value).strip() == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


async def get_lookup_id(table_class: Type[Table], key: str) -> Optional[int]:
    """Holt die ID für einen Lookup-Wert basierend auf dem Key."""
    if not key:
        return None

    # Mapping anwenden falls vorhanden
    table_name = table_class.__name__.lower()
    if table_name in FIELD_MAPPINGS:
        key = FIELD_MAPPINGS[table_name].get(key, key)

    try:
        if hasattr(table_class, 'key'):
            record = await table_class.select(table_class.id).where(table_class.key == key).first()
        elif hasattr(table_class, 'code'):
            record = await table_class.select(table_class.id).where(table_class.code == int(key)).first()
        else:
            return None

        return record['id'] if record else None
    except Exception as e:
        print(
            f"Fehler beim Lookup für {table_class.__name__} mit key {key}: {e}")
        return None


async def insert_default_data_for_table(table_class: Type[Table], data_list: List[Dict[str, Any]]) -> None:
    """Generische Funktion zum Einfügen von Standarddaten für eine Tabelle."""
    table_name = table_class.__name__

    for data_item in data_list:
        # Prüfen ob bereits vorhanden
        if "key" in data_item:
            existing = await table_class.exists().where(table_class.key == data_item["key"])
        elif "code" in data_item:
            existing = await table_class.exists().where(table_class.code == data_item["code"])
        else:
            existing = await table_class.exists().where(table_class.name == data_item["name"])
        if not existing:
            await table_class.insert(table_class(**data_item))
            print(f"{table_name} '{data_item['name']}' eingefügt.")


async def initialize_default_data():
    """Fügt Standarddaten für alle konfigurierten Tabellen ein, falls sie nicht vorhanden sind."""

    for table_class, data_list in DEFAULT_DATA_CONFIG.items():
        await insert_default_data_for_table(table_class, data_list)


async def initialize_all_data(json_file_path: str = None):
    """Initialisiert alle Daten: Lookup-Tabellen und optional Ghostbike-Import."""

    # Zuerst Lookup-Tabellen initialisieren
    print("Initialisiere Lookup-Tabellen...")
    await initialize_default_data()

    # Optional: Ghostbike-Daten importieren
    if json_file_path and os.path.exists(json_file_path):
        print(f"Importiere Ghostbike-Daten aus {json_file_path}...")
        await import_ghostbike_from_json(json_file_path)
    else:
        print("Kein JSON-Import durchgeführt.")


async def import_ghostbike_from_json(json_file_path: str) -> None:
    """Importiert Ghostbike-Daten aus der JSON-Datei."""

    if not os.path.exists(json_file_path):
        print(f"JSON-Datei nicht gefunden: {json_file_path}")
        return

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ghostbike_data = data.get("GB HH", [])
    print(f"Importiere {len(ghostbike_data)} Ghostbike-Einträge...")

    imported_count = 0
    skipped_count = 0

    for item in ghostbike_data:
        ghostbike_data_entry = {}
        # Nur vollständige Einträge mit Index verarbeiten
        if not item.get("Index"):
            skipped_count += 1
            continue

        try:
            # Prüfen ob bereits vorhanden
            existing = await Ghostbike.exists().where(
                Ghostbike.radunfall_index == item["Index"]
            )
            if existing:
                print(
                    f"Ghostbike {item['Index']} bereits vorhanden, überspringe...")
                skipped_count += 1
                continue

            # Lookup-IDs holen
            street_type_id = await get_lookup_id(StreetType, clean_string(item.get("Straße*")))
            accident_type_id = await get_lookup_id(AccidentType, clean_string(item.get("Typ*")))
            location_type_id = await get_lookup_id(LocationType, clean_string(item.get("Ortslage*")))
            opponent_id = await get_lookup_id(Opponent, clean_string(item.get("Gegner")))
            infrastructure_id = await get_lookup_id(Infrastructure, clean_string(item.get("Wegart*")))
            main_fault_id = await get_lookup_id(MainFault, clean_string(item.get("Hauptschuld*")))
            accident_code = int(
                item["Key**"]) if item.get("Key**") and item["Key**"] != "NaN" else None

            # Ghostbike-Eintrag erstellen
            ghostbike_data_entry = {
                "radunfall_index": item["Index"],
                "accident_date": parse_date(item.get("Datum")),
                # Gleich wie accident_date, da Todesdatum
                "death_date": None,
                "address": clean_string(item.get("Adresse")),
                "postal_code": clean_string(int(item.get("PLZ"))),
                "location": clean_string(item.get("Ort + PM")) or "Hamburg",
                "location_population": clean_number(item.get("EW")),
                "street_type": street_type_id,
                "accident_type": accident_type_id,
                "location_type": location_type_id,
                "accident_description": clean_string(item.get("Kommentar*")),
                "gender": clean_string(item.get("Sex")),
                "age": None,
                "pedelec": None,  # Nicht in den Daten vorhanden
                "opponent": opponent_id,
                "infrastructure": infrastructure_id,
                "main_fault": main_fault_id,
                "accident_code": accident_code,
                "status": 1,  # StatusEnum.okay
                "status_text": '',
                "status_checked_date": parse_date(item.get("Datum")),
                "latitude": clean_number(item.get("GPX-LAT")),
                "longitude": clean_number(item.get("GPX-LON")),
                "osm_memorial_id": -1,
            }
            age = clean_number(item.get("Alter"))
            if age is not None and not math.isnan(age):
                ghostbike_data_entry["age"] = int(age)
            if ghostbike_data_entry["address"] is None:
                ghostbike_data_entry["address"] = ""

            if ghostbike_data_entry["latitude"] is None or ghostbike_data_entry["longitude"] is None:
                google_url = item.get("Wegart*_hyperlink")
                if google_url:
                    google_pattern = r'@(-?\d+\.?\d*),(-?\d+\.?\d*),\d+m?'
                    match = re.search(google_pattern, google_url)
                    if match:
                        ghostbike_data_entry["latitude"] = clean_number(
                            match.group(1))
                        ghostbike_data_entry["longitude"] = clean_number(
                            match.group(2))
                if ghostbike_data_entry["latitude"] is None or ghostbike_data_entry["longitude"] is None:
                    osm_url = item.get("OSM-Link_text_link")
                    if osm_url:
                        osm_pattern = r'mlat=(-?\d+\.?\d*)&mlon=(-?\d+\.?\d*)'
                        match = re.search(osm_pattern, osm_url)
                        if match:
                            ghostbike_data_entry["latitude"] = clean_number(
                                match.group(1))
                            ghostbike_data_entry["longitude"] = clean_number(
                                match.group(2))
            gb = await Ghostbike.insert(Ghostbike(**ghostbike_data_entry))
            print(f"Ghostbike {item['Index']} ({gb[0]['id']}) importiert.")
            imported_count += 1
            presse_url = item["Ort + PM_hyperlink"].replace(
                "http://", "https://")
            medium_id = await get_medium_id_from_url(presse_url)
            await NewspaperArticle.insert(
                NewspaperArticle({
                    "ghostbike": gb[0]['id'],
                    "medium": medium_id,
                    "primary": True,
                    "url": presse_url,
                    "date": date(1970, 1, 1)
                })
            )
            print(f"Presseartikel für Ghostbike {item['Index']} importiert.")

        except Exception as e:
            print(
                f"Fehler beim Import von Ghostbike {item.get('Index', 'unknown')}: {e}")
            print(ghostbike_data_entry)
            print(item)
            skipped_count += 1

    print(
        f"Import abgeschlossen: {imported_count} importiert, {skipped_count} übersprungen.")
