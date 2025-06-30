import pandas as pd
import json
import numpy as np
import openpyxl


def _get_link_if_exists(cell) -> str | None:
    """Extrahiert Hyperlink aus einer Excel-Zelle, falls vorhanden."""
    try:
        return cell.hyperlink.target
    except AttributeError:
        return None


def excel_to_json_with_links(excel_path, json_path):
    excel_file = pd.ExcelFile(excel_path)
    sheets = excel_file.sheet_names
    all_sheets_data = {}

    # Lade auch die openpyxl Workbook für Link-Extraktion
    wb = openpyxl.load_workbook(excel_path)

    for sheet in sheets:
        # Lese Zeile 4 als Header (header=3, da 0-basiert)
        df = pd.read_excel(excel_file, sheet_name=sheet, header=3)
        ws = wb[sheet]

        # Entferne komplett leere Zeilen
        df = df.dropna(how='all')

        # Konvertiere DataFrame zu Records
        data = df.where(pd.notnull(df), None).to_dict(orient='records')

        # Durchsuche alle Zellen nach Hyperlinks
        for row_idx, record in enumerate(data):
            # Sammle alle Link-Informationen erst, bevor wir das Dictionary ändern
            links_to_add = {}

            # Durchsuche alle Spalten in dieser Zeile
            for col_idx, (col_name, cell_value) in enumerate(record.items()):
                # Excel-Zeile ist row_idx + 5 (wegen 4 Headerzeilen und 1-basierter Indexierung)
                # Excel-Spalte ist col_idx + 1 (1-basierte Indexierung)
                try:
                    excel_cell = ws.cell(row=row_idx + 5, column=col_idx + 1)
                    hyperlink = _get_link_if_exists(excel_cell)
                    if hyperlink:
                        # Sammle Link-Information
                        link_field_name = f"{col_name}_hyperlink"
                        links_to_add[link_field_name] = hyperlink
                        print(
                            f"Hyperlink gefunden in {sheet}, Zeile {row_idx + 5}, Spalte {col_name}: {hyperlink}")
                except Exception as e:
                    # Ignoriere Fehler bei ungültigen Zellreferenzen
                    continue

                # Zusätzlich: Prüfe auch auf HTTP-Links im Zelltext (fallback)
                if isinstance(cell_value, str) and cell_value.startswith('http'):
                    link_field_name = f"{col_name}_hyperlink"
                    if link_field_name not in links_to_add:  # Nur wenn noch kein Hyperlink gefunden
                        links_to_add[f"{col_name}_text_link"] = cell_value
                        print(
                            f"Text-Link gefunden in {sheet}, Zeile {row_idx + 5}, Spalte {col_name}: {cell_value}")

            # Jetzt alle gefundenen Links zum Record hinzufügen
            record.update(links_to_add)

        all_sheets_data[sheet] = data

    def json_converter(o):
        if isinstance(o, (pd.Timestamp, pd.Timedelta)):
            return str(o)
        elif isinstance(o, np.generic):
            return o.item()
        return str(o)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_sheets_data, f, indent=2,
                  ensure_ascii=False, default=json_converter)


if __name__ == "__main__":
    excel_path = 'Ghostbike-Hamburg-Tabelle.xlsx'
    json_path = 'Ghostbike-Hamburg-Tabelle.json'
    excel_to_json_with_links(excel_path, json_path)
    print(f'Konvertierung abgeschlossen. JSON gespeichert unter: {json_path}')
