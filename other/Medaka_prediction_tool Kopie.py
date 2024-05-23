import json
from datetime import datetime, timedelta
import re
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import pandas as pd

# Entwicklungszeiten für Stadien bei 26°C
stadien_zeiten_26C = {
    0: 0, 1: 0.05, 2: 0.5, 3: 1.08, 4: 1.75, 5: 2.33, 6: 2.92, 7: 3.5,
    8: 4.08, 9: 5.25, 10: 6.5, 11: 8.25, 12: 10.33, 13: 13, 14: 15, 15: 17.5,
    16: 21, 17: 25, 18: 26, 19: 27.5, 20: 31.5, 21: 34, 22: 38, 23: 41, 24: 44,
    25: 50, 26: 54, 27: 58, 28: 64, 29: 74, 30: 82, 31: 95, 32: 101, 33: 106,
    34: 121, 35: 132, 36: 144, 37: 168, 38: 192, 39: 216
}

dateipfad = 'entwicklungszeiten.json'

# Hilfsfunktion, um einen Wochentag in eine Zahl umzuwandeln (Montag = 0, ..., Sonntag = 6)
def parse_weekday(weekday_str):
    days = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    return days.index(weekday_str)

# Funktion, um die Wochentage des Nutzers zu parsen
def parse_lab_days(lab_days_str):
    # Prüft, ob der String leer ist, und gibt in diesem Fall eine leere Liste zurück
    if not lab_days_str.strip():
        return []
    # Ansonsten wird die ursprüngliche Logik ausgeführt
    days = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    return [days.index(day.strip()) for day in lab_days_str.split(',')]

def parse_lab_hours(lab_hours_str):
    if not lab_hours_str.strip():
        return None, None
    try:
        start_hour, end_hour = map(int, re.findall(r'\d+', lab_hours_str))
        return time(start_hour), time(end_hour)
    except ValueError:
        print("Das Format der Laborzeiten ist ungültig. Bitte geben Sie die Zeiten im Format HH-HH an.")
        return None, None
    
def parse_collection_window(collection_window_str):
    if not collection_window_str.strip():
        return None, None  # Wenn keine Eingabe, gebe None zurück
    try:
        start_str, end_str = collection_window_str.split("-")
        start = datetime.strptime(start_str, "%H").time()
        end = datetime.strptime(end_str, "%H").time()
        return start, end
    except ValueError:
        print("Das Format des Sammelzeitfensters ist ungültig. Bitte geben Sie das Zeitfenster im Format HH-HH an.")
        return None, None

# Funktion, um die Startzeit der Eiablage zu parsen
def parse_start_time(start_time_str):
    if not start_time_str.strip():
        return None, None, None
    try:
        start_datetime = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
        collection_day = start_datetime.weekday()
        collection_time = start_datetime.time()
        return collection_day, collection_time, start_datetime
    except ValueError:
        print("Das Format des Starttermins ist ungültig. Bitte verwenden Sie das Format YYYY-MM-DD HH:MM.")
        return None, None, None

# Funktion, um die gewünschten Stadien zu parsen
def parse_required_stages(required_stages_str):
    if not required_stages_str.strip():
        return None # Gibt None zurück, wenn die Eingabe leer ist
    try:
        return list(map(int, required_stages_str.split(',')))
    except ValueError:
        return None # Gibt None zurück, wenn die Eingabe leer ist

# Funktion, um die gewünschte Zeitspanne zu parsen
def parse_desired_time_window(desired_time_window_str):
    try:
        hours = int(desired_time_window_str.split()[0])  # Annahme, dass die Eingabe in Stunden ist
        return hours
    except (ValueError, IndexError):
        print("Das Format der Zeitspanne ist ungültig. Bitte geben Sie die Anzahl der Stunden an.")
        return None

def parse_desired_time(desired_time_str):
    try:
        # Versuche, den String in ein datetime Objekt umzuwandeln
        return datetime.strptime(desired_time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        # Gib einen Fehler aus und kehre None zurück, falls das Format ungültig ist
        print("Das Format des Wunschtermins ist ungültig. Bitte verwenden Sie das Format YYYY-MM-DD HH:MM.")
        return None

    daten = daten_laden(dateipfad)
    punkte, werte = vorbereiten_der_daten(daten)
    
    # Erstelle ein Gitter basierend auf den angegebenen Temperatur- und Stadiumsbereichen für die Interpolation
    grid_temperatur, grid_stadium = np.meshgrid(temperatur_range, stadium_range)
    grid_punkte = np.vstack([grid_temperatur.ravel(), grid_stadium.ravel()]).T
    
    # Führe die Interpolation durch
    geschätzte_zeiten = griddata(punkte, werte, grid_punkte, method='cubic').reshape(grid_temperatur.shape)
    
    return geschätzte_zeiten

def parse_available_temperatures(available_temperatures_str):
    if not available_temperatures_str.strip():
        return []  # Keine Temperaturen angegeben, gebe leere Liste zurück
    try:
        temperatures = [float(temp) for temp in available_temperatures_str.split(',')]
        return temperatures
    except ValueError:
        print("Das Format der Temperaturangaben ist ungültig. Bitte geben Sie die Temperaturen in Grad Celsius an, getrennt durch Kommas (z.B. 24,26,28).")
        return None


def daten_laden(dateipfad):
    try:
        with open(dateipfad, 'r') as datei:
            daten = json.load(datei)
            # Stelle sicher, dass die geladenen Daten das erwartete Format haben
            if "temperaturen" in daten:
                return daten
            else:
                # Wenn "temperaturen" nicht im Wurzelobjekt ist, initialisiere die Struktur
                return {"temperaturen": []}
    except FileNotFoundError:
        # Wenn die Datei nicht existiert, initialisiere die Struktur
        return {"temperaturen": []}

def daten_speichern(dateipfad, daten):
    print(f"Speichere Daten: {daten}")
    with open(dateipfad, 'w') as datei:
        json.dump(daten, datei, indent=4)

def vorbereiten_der_daten(daten):
    # This will store each entry as a dictionary in a list
    daten_liste = []
    for temperatur_info in daten['temperaturen']:
        temperatur = float(temperatur_info['temperatur'])
        for stadium_info in temperatur_info['stadien']:
            stadium = float(stadium_info['stadium'])
            zeiten = [float(zeit) for zeit in stadium_info['zeiten']]
            mittlere_zeit = np.mean(zeiten) if zeiten else np.nan
            daten_liste.append({
                'Temperatur': temperatur,
                'Stadium': stadium,
                'Mittlere_Zeit': mittlere_zeit
            })
    
    # Convert the list of dictionaries to a DataFrame
    daten_df = pd.DataFrame(daten_liste)
    return daten_df

# Assuming 'daten' is your JSON loaded as a dictionary
# daten_df = vorbereiten_der_daten(your_json_data)
# print(daten_df.head())

def interpoliere_daten(df, resolution=100):
    # Extract arrays from DataFrame
    punkte = df[['Temperatur', 'Stadium']].values
    werte = df['Mittlere_Zeit'].values
    
    # Determine the range for temperatures and stages
    temp_min, temp_max = np.min(punkte[:, 0]), np.max(punkte[:, 0])
    stadium_min, stadium_max = np.min(punkte[:, 1]), np.max(punkte[:, 1])
    
    # Create a grid for interpolation
    temp_grid, stadium_grid = np.mgrid[temp_min:temp_max:complex(resolution), stadium_min:stadium_max:complex(resolution)]
    
    # Perform 2D interpolation using cubic spline
    werte_grid = griddata(punkte, werte, (temp_grid, stadium_grid), method='cubic')
    
    return temp_grid, stadium_grid, werte_grid


def plot_interpolierte_daten(temp_grid, stadium_grid, werte_grid, available_temperatures):
    plt.figure(figsize=(14, 10))

    # Iterate over each temperature and plot the average value
    for temp_index, temp in enumerate(temp_grid[0, :]):
        if temp in available_temperatures:  # Direct comparison for exact match
            stadium_values = stadium_grid[:, temp_index]
            entwicklung_values = werte_grid[:, temp_index]

            # Calculate the average developmental times for each stage
            durchschnittliche_entwicklung = np.nanmean(entwicklung_values, axis=0)

            plt.plot(durchschnittliche_entwicklung, stadium_values, label=f"{temp:.1f}°C")

    plt.gca().invert_yaxis()
    plt.xlabel('Development Time in Hours')
    plt.ylabel('Stage')
    plt.ylim(50, 0)
    plt.xlim(left=0)
    plt.title('Interpolated Development Duration vs. Stage at Selected Temperatures')
    plt.legend(title='Temperature')
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.show()



# Hauptfunktion um Daten einzutragen
def entwicklung_hinzufuegen(dateipfad, temperatur, stadium, zeit_in_hpf):
    daten = daten_laden(dateipfad)
    # Überprüfe, ob die Temperatur bereits existiert
    temp_eintrag = None
    for temp in daten["temperaturen"]:
        if temp["temperatur"] == temperatur:
            temp_eintrag = temp
            break

    # Falls die Temperatur noch nicht existiert, füge sie hinzu
    if not temp_eintrag:
        temp_eintrag = {"temperatur": temperatur, "stadien": []}
        daten["temperaturen"].append(temp_eintrag)
    
    # Überprüfe, ob das Stadium bereits existiert
    stadium_eintrag = None
    for st in temp_eintrag["stadien"]:
        if st["stadium"] == stadium:
            stadium_eintrag = st
            break
    
    # Falls das Stadium noch nicht existiert, füge es hinzu
    if not stadium_eintrag:
        stadium_eintrag = {"stadium": stadium, "zeiten": []}
        temp_eintrag["stadien"].append(stadium_eintrag)
    
    # Füge die Zeit in HPF hinzu
    stadium_eintrag["zeiten"].append(zeit_in_hpf)
    
    # Speichere die aktualisierten Daten
    daten_speichern(dateipfad, daten)
    print("Daten erfolgreich hinzugefügt.")

def mehrere_entwicklungen_hinzufuegen(dateipfad, entwicklungen):
    daten = daten_laden(dateipfad)
    for temperatur, stadien in entwicklungen.items():
        for stadium, zeit_in_hpf in stadien.items():
            entwicklung_hinzufuegen(dateipfad, temperatur, stadium, zeit_in_hpf)
    print("Alle Entwicklungsdaten wurden erfolgreich hinzugefügt.")


# Funktion, um vom Nutzer gewünschte Stadien zu sammeln
def get_user_input():
    # Erste Frage: Gewünschte Stadien
    required_stages = None
    while required_stages is None:
        required_stages_str = input("Welche Stadien benötigen Sie? (Nummern getrennt durch Kommas, z.B. 5,10,15): ")
        required_stages = parse_required_stages(required_stages_str)
        if required_stages is None:
            print("Bitte geben Sie mindestens ein gültiges Stadium an. Das Format ist ungültig oder die Eingabe war leer.")

    # Zweite Frage: Eiersammel-Datum
    start_time_str = input("Bitte geben Sie das genaue Datum und Uhrzeit des Eiersammelns an (YYYY-MM-DD HH:MM) oder lassen Sie das Feld leer: ")
    if start_time_str.strip():  # Überprüfe, ob die Eingabe nicht leer ist
        _, _, start_datetime = parse_start_time(start_time_str)
        while start_datetime is None:
            print("Das Format des Starttermins ist ungültig. Bitte verwenden Sie das Format YYYY-MM-DD HH:MM.")
            start_time_str = input("Bitte geben Sie das genaue Datum und Uhrzeit des Eiersammelns an (YYYY-MM-DD HH:MM): ")
            _, _, start_datetime = parse_start_time(start_time_str)
    else:
        start_datetime = None  # Erlaubt das Leerlassen des Feldes

    # Dritte Frage: Gleichzeitiges Erreichen aller Stadien
    same_time_window_str = input("Gibt es ein Zeitfenster, in dem alle Stadien gleichzeitig erreicht werden sollen? (Ja/Nein): ") or "Nein"
    
    desired_time_str = ""
    desired_time_window_str = ""
    if same_time_window_str.lower() == "ja":
        desired_time_str = input("Bitte geben Sie das gewünschte Datum und Uhrzeit an, wann die Stadien erreicht werden sollen (z.B. 2023-07-04 15:00): ") or ""
        desired_time_window_str = input("Bitte geben Sie die Zeitspanne an diesem Tag an (z.B. 2 Stunden): ") or ""

    #  Vierte Frage: Neue Abfrage nach den verfügbaren Temperaturen
    available_temperatures_str = ""
    if start_time_str.strip() or desired_time_str.strip():
        while not available_temperatures_str.strip():
            available_temperatures_str = input("Bitte geben Sie die verfügbaren Temperaturen an (Grad Celsius, getrennt durch Kommas, z.B. 24,26,28): ")
    else:
        available_temperatures_str = input("Bitte geben Sie die verfügbaren Temperaturen an (Grad Celsius, getrennt durch Kommas, z.B. 24,26,28) oder lassen Sie das Feld leer: ")

    available_temperatures = [float(temp) for temp in available_temperatures_str.split(",")] if available_temperatures_str.strip() else []

    # Fünfte Frage: Zeitfenster für Eiersammlung
    collection_window_str = input("Gibt es ein spezifisches Zeitfenster für das Eiersammeln? (z.B. 10-11) oder leer lassen: ") or ""

    # Sechste Frage: Verfügbarkeit im Labor
    lab_days_str = input("An welchen Wochentagen sind Sie im Labor? (z.B. Mo,Di,Mi,Do,Fr) oder leer lassen: ") or ""
    
    lab_hours_str = input("In welcher Zeitspanne sind Sie täglich im Labor? (z.B. 9-18) oder leer lassen: ") or ""
    
    return (required_stages_str, start_time_str, same_time_window_str, desired_time_str, 
            desired_time_window_str, collection_window_str, lab_days_str, lab_hours_str, available_temperatures_str)
    # Konvertieren Sie die Eingaben in ein brauchbares Format
    # Diese Funktion muss noch implementiert werden
    # ...


def berechne_stadien(required_stages, stadien_zeiten_26C, start_datetime):
    print("Startzeit angegeben. Berechnung der genauen Zeitpunkte für das Erreichen der Stadien bei 26°C.")
    for stage in required_stages:
        if stage in stadien_zeiten_26C:
            reach_datetime = start_datetime + timedelta(hours=stadien_zeiten_26C[stage])
            print(f"Stadium {stage} wird am {reach_datetime.strftime('%Y-%m-%d %H:%M')} bei 26°C erreicht.")
        else:
            print(f"Stadium {stage} hat keine festgelegte Entwicklungszeit bei 26°C.")

def zeige_dauer_fuer_stadien(required_stages, dateipfad, available_temperatures):
    # Lade Daten und bereite sie für die Interpolation vor
    daten = daten_laden(dateipfad)
    punkte, werte = vorbereiten_der_daten(daten)

    # Definiere Standardtemperatur und -stadienbereich
    standard_temperatur = [26] if available_temperatures is None else available_temperatures
    stadium_range = np.array(required_stages)
    
    # Interpoliere Entwicklungszeiten für angegebene Temperaturen oder 26°C
    for temperatur in standard_temperatur:
        geschätzte_zeiten = griddata(punkte, werte, (np.array([temperatur] * len(stadium_range)), stadium_range), method='cubic')
        print(f"\nDauer bis zum Erreichen der Stadien bei {temperatur}°C:")
        for stadium, zeit in zip(stadium_range, geschätzte_zeiten):
            if np.isnan(zeit):
                print(f"Stadium {stadium}: Keine Daten verfügbar.")
            else:
                print(f"Stadium {stadium} wird nach {zeit:.2f} Stunden erreicht.")

def berechne_rueckwaerts_vom_wunschtermin(required_stages, stadien_zeiten, wunschtermin_str, start_datetime):
    wunschtermin = datetime.strptime(wunschtermin_str, "%Y-%m-%d %H:%M")

    # Sammelzeitpunkte für jedes Stadium berechnen
    for stage in required_stages:
        if stage in stadien_zeiten:
            entwicklungszeit = stadien_zeiten[stage]
            sammelzeitpunkt = wunschtermin - timedelta(hours=entwicklungszeit)
            if sammelzeitpunkt < start_datetime:
                print(f"Für Stadium {stage} ist der Sammelzeitpunkt ({sammelzeitpunkt.strftime('%Y-%m-%d %H:%M')}) in der Vergangenheit. Planung nicht möglich.")
            else:
                print(f"Um Stadium {stage} bis zum {wunschtermin_str} zu erreichen, müssen die Eier spätestens am {sammelzeitpunkt.strftime('%Y-%m-%d %H:%M')} gesammelt werden.")
        else:
            print(f"Keine Entwicklungszeit für Stadium {stage} definiert.")

# Hauptfunktion für das Vorhersagetool
def prediction_tool():
    (required_stages_str, start_time_str, same_time_window_str, desired_time_str, 
     desired_time_window_str, collection_window_str, lab_days_str, lab_hours_str, available_temperatures_str) = get_user_input()
    
    # Konvertierung der Eingaben in brauchbare Formate
    # Verwende die Variablen direkt, ohne sie vorher zu definieren
    required_stages = parse_required_stages(required_stages_str)
    collection_day, collection_time, start_datetime = parse_start_time(start_time_str)
    lab_days = parse_lab_days(lab_days_str)
    lab_start_time, lab_end_time = parse_lab_hours(lab_hours_str)
    collection_start, collection_end = parse_collection_window(collection_window_str)
    desired_time = parse_desired_time(desired_time_str) if desired_time_str else None
    desired_time_window = parse_desired_time_window(desired_time_window_str) if desired_time_window_str else None
    available_temperatures = parse_available_temperatures(available_temperatures_str)

    daten = daten_laden(dateipfad)

    punkte, werte = vorbereiten_der_daten(daten)
    temp_grid, stadium_grid, werte_grid = interpoliere_daten(punkte, werte, resolution=100)


    # Logik basierend auf den gegebenen Eingaben
    if desired_time_str and start_datetime:
        # Wunschtermin für das gleichzeitige Erreichen aller Stadien ist angegeben
        print("Wunschtermin angegeben. Berechnung der Sammelzeitpunkte, um alle Stadien gleichzeitig zu erreichen.")
        berechne_rueckwaerts_vom_wunschtermin(required_stages, stadien_zeiten_26C, desired_time_str, start_datetime)
    elif start_datetime:
        # Startzeit ist angegeben, aber kein Wunschtermin
        print("Startzeit angegeben. Berechnung der genauen Zeitpunkte für das Erreichen der Stadien bei 26°C.")
        berechne_stadien(required_stages, stadien_zeiten_26C, start_datetime)
    else:
        # Nur die Stadien sind angegeben
        print("Nur Stadien angegeben. Anzeige der Dauer bis zum Erreichen der Stadien bei 26°C.")
        zeige_dauer_fuer_stadien(required_stages, dateipfad, available_temperatures)

    # Logik zur Berechnung der besten Zeiten, um die Stadien zu erreichen
    # Diese Funktion muss noch implementiert werden
    # ...

    #plot_interpolierte_daten(temp_grid, stadium_grid, werte_grid, available_temperatures)
   


    # Ergebnisse ausgeben
    # ...

    # Ausgabe der konvertierten Daten
    print("Labortage:", lab_days)
    print("Tag der Eiablage:", collection_day) 
    if start_datetime:  # Prüfe, ob ein Startdatum angegeben wurde
        print(f"Tag der Eiablage: {start_datetime.strftime('%Y-%m-%d')}, Uhrzeit der Eiablage: {collection_time}")
    else:
        print("Kein Eiersammel-Datum angegeben.")
    print("Laborzeiten:", lab_start_time, lab_end_time)
    print("Benötigte Stadien:", required_stages)


def main():
    aktion = input("Wollen Sie 'Medaka Stages predicten' oder 'Daten eintragen'? (predicten/eintragen): ")
    
    
    if aktion.lower() == "eintragen":
        eintrag_aktion = input("Wollen Sie 'einen Eintrag' oder 'mehrere Einträge' machen? (einen/mehrere): ")
        if eintrag_aktion.lower() == "einen":
            temperatur = input("Temperatur: ")
            stadium = input("Stadium: ")
            dauer_in_hpf = input("Dauer in HPF: ")
            entwicklung_hinzufuegen(dateipfad, temperatur, stadium, dauer_in_hpf)
        elif eintrag_aktion.lower() == "mehrere":
            entwicklungsdaten = input("Geben Sie mehrere Entwicklungsdaten ein (Format: 'Temperatur,Stadium,Dauer; Temperatur,Stadium,Dauer; ...'): ")
            entwicklungsdaten_liste = entwicklungsdaten.split(";")
            for datensatz in entwicklungsdaten_liste:
                daten = datensatz.strip().split(",")
                if len(daten) == 3:
                    temperatur, stadium, dauer_in_hpf = daten
                    entwicklung_hinzufuegen(dateipfad, temperatur.strip(), stadium.strip(), dauer_in_hpf.strip())
                else:
                    print("Fehlerhafter Datensatz übersprungen:", datensatz)

    elif aktion.lower() == "predicten":
        prediction_tool()
    else:
        print("Unbekannte Aktion. Bitte wählen Sie 'predicten' oder 'eintragen'.")

if __name__ == "__main__":
    main() 

