from ghostbike.tables import Infrastructure, MainFault, AccidentCode, LocationType, Opponent, StreetType

default_opponents = [
    {"key": "r", "name": "Radfahrende"},
    {"key": "g", "name": "Kraftfahrender Gegner"},
    {"key": "s", "name": "Alleinunfall"},
    {"key": "f", "name": "Fußgänger/Haustier"},
    {"key": "o", "name": "Schuld offen"},
]

default_location_types = [
    {"key": "i", "name": "innerorts"},
    {"key": "o", "name": "außerorts"},
]

default_infrastructure = [
    {"key": "FB", "name": "nur Fahrbahn vorhanden"},
    {"key": "RVA", "name": "straßenbegleitende Radverkehrsanlage vorhanden"},
    {"key": "Weg", "name": "Weg ohne öffentlichen KFZ-Verkehr"},
]

default_main_faults = [
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
]

default_street_types = [
    {"key": "b", "name": "Bundesstraße"},
    {"key": "l", "name": "Landes-/Staatsstraße"},
    {"key": "k", "name": "Kreisstraße, Ortsverbindungsstraße"},
    {"key": "v", "name": "Vorfahrtstraße innerorts"},
    {"key": "n", "name": "Nebenstraße innerorts"},
]

default_accident_codes = [
    {"key": 141, "name": "Ohne Mitwirkende Besonderheiten von Querschnitt und Längsneigung Gerade"},
    {"key": 149, "name": "Ohne Mitwirkende Besonderheiten von Querschnitt und Längsneigung"},
    {"key": 189, "name": "Straßenverlauf nicht bekannt"},
    {"key": 199, "name": "Sontiger Fahrunfall"},
    {"key": 211, "name": "Linksabbieger in gleiche Richtung"},
    {"key": 224, "name": "Linksabbieger in Gegenrichtung"},
    {"key": 241, "name": "Rechtsabbieger in gleiche Richtung"},
    {"key": 243, "name": "Rechtsabbieger in gleiche Richtung"},
    {"key": 244, "name": "Rechtsabbieger in Gegenrichtung"},
    {"key": 261, "name": "Linksabbieger Wartepflichtiger"},
    {"key": 299, "name": "Sonstiger Abbigeunfall"},
    {"key": 341, "name": "Bevorrechtiges Fahrzeug, Radweg von links"},
    {"key": 373, "name": "Radwegaufleitung von Rechts"},
    {"key": 379, "name": "Einfahrender Radfaher, Richtung unklar"},
    {"key": 399, "name": "Sonstige Einbiegeunfall"},
    {"key": 499, "name": "Sonstige Überschreiten-Unfall"},
    {"key": 599, "name": "Sontiger Ruhender Verkehr Unfall"},
    {"key": 601, "name": "Vorrausfahrender Einspurig"},
    {"key": 646, "name": "Spurwechsler nach rechts nach Überholen auf Richtungsfahrbahn"},
    {"key": 699, "name": "Sonstiger Unfall im Längsverkehr"},
    {"key": 762, "name": "Schwächeanfall"},
    {"key": 799, "name": "Sonstiger Unfall"},
]


async def initialize_default_data():
    """Fügt Standarddaten in die Opponent-Tabelle ein, falls sie nicht vorhanden sind."""

    for opponent_data in default_opponents:
        # Prüfen ob bereits vorhanden
        existing = await Opponent.exists().where(Opponent.key == opponent_data["key"])
        if not existing:
            await Opponent.insert(Opponent(**opponent_data))
            print(f"Opponent '{opponent_data['name']}' eingefügt.")

    for location_data in default_location_types:
        # Prüfen ob bereits vorhanden
        existing = await LocationType.exists().where(LocationType.key == location_data["key"])
        if not existing:
            await LocationType.insert(LocationType(**location_data))
            print(f"LocationType '{location_data['name']}' eingefügt.")

    for infrastructure_data in default_infrastructure:
        # Prüfen ob bereits vorhanden
        existing = await Infrastructure.exists().where(Infrastructure.key == infrastructure_data["key"])
        if not existing:
            await Infrastructure.insert(Infrastructure(**infrastructure_data))
            print(f"Infrastucture '{infrastructure_data['name']}' eingefügt.")

    for fault_data in default_main_faults:
        existing = await MainFault.exists().where(MainFault.key == fault_data["key"])
        if not existing:
            await MainFault.insert(MainFault(**fault_data))
            print(f"MainFault '{fault_data['name']}' eingefügt.")

    # StreetType Standarddaten

    for street_data in default_street_types:
        existing = await StreetType.exists().where(StreetType.key == street_data["key"])
        if not existing:
            await StreetType.insert(StreetType(**street_data))
            print(f"StreetType '{street_data['name']}' eingefügt.")
    for accident_code in default_accident_codes:
        existing = await AccidentCode.exists().where(AccidentCode.key == accident_code["key"])
        if not existing:
            await AccidentCode.insert(AccidentCode(**accident_code))
            print(f"AccidentCode '{accident_code['name']}' eingefügt.")
