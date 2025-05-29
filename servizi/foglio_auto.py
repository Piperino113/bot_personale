import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

CREDENZIALI_PATH = 'Credenziali/bot-auto-459105-30abe67cb12b.json'
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credenziali = ServiceAccountCredentials.from_json_keyfile_name(CREDENZIALI_PATH, SCOPE)
client = gspread.authorize(credenziali)

def salva_dati_rifornimento(data, litri, spesa, km, note=""):
    foglio = client.open("Gestione auto").worksheet("Rifornimenti")
    foglio.append_row([data, litri, spesa, "", km, "", note])

    foglio_chilometri = client.open("Gestione auto").worksheet("Chilometraggio")
    foglio_chilometri.append_row([data, km])

    consumo = calcola_consumo()
    prezzo_litro = calcola_prezzo()


    # aggiorniamo la riga del rifornimento appena inserita (ultima riga)
    righe = len(foglio.get_all_values())
    foglio.update_cell(righe, 6, round(consumo, 2))  # colonna 6 = 'consumo'

    # aggiorniamo la riga del prezzo al litro del rifornimento appena fatoo
    righe = len(foglio .get_all_values())
    foglio.update_cell(righe, 4, round(prezzo_litro,2))
    return f"Rifornimento salvato con successo."

def salva_dati_spese(data, descrizione, importo):
    foglio = client.open("Gestione auto").worksheet("Spese")
    foglio.append_row([data, descrizione, importo])
    return "Spesa salvata con successo."

def salva_dati_chilometraggio(data, km):
    foglio = client.open("Gestione auto").worksheet("Chilometraggio")

    gg_totali = calcola_gg_totali()
    gg_rimanenti = calcola_gg_rimanenti()
    km_riconsegna = calcola_km_riconsegna(km, gg_totali, gg_rimanenti)

    foglio.append_row([data, km, round(km_riconsegna, 2)])

    return f"Chilometraggio salvato con successo. KM previsti alla riconsegna: {km_riconsegna:.2f}"


def calcola_consumo():
    foglio_rif = client.open("Gestione auto").worksheet("Rifornimenti")
    dati = foglio_rif.get_all_records()
    if len(dati) < 2:
        return 0.0
    try:
        totale_km = int(dati[-1]['km'])
    except (KeyError, ValueError) as e:
        return 0.0
    try:
        totale_litri = sum(float(r['litri']) for r in dati[0:])  
    except (KeyError, ValueError) as e:
        return 0.0
    if totale_litri == 0:
        return 0.0
    consumo = totale_km / totale_litri
    return consumo

def calcola_prezzo():
    foglio_rif = client.open("Gestione auto").worksheet("Rifornimenti")
    dati = foglio_rif.get_all_records()
    if len(dati) < 2:
        return 0.0
    try:
        litri = int(dati[-1]['litri'])
    except (KeyError, ValueError) as e:
        return 0.0
    try:
        soldi = int(dati[-1]['euro'])
    except (KeyError, ValueError) as e:
        return 0.0
    prezzo_litro = soldi / litri
    return prezzo_litro

def calcola_gg_totali():
    foglio_rif = client.open("Gestione auto").worksheet("Chilometraggio")
    dati = foglio_rif.get_all_records()

    if len(dati) < 2:
        return 0

    # Estrai le date in formato stringa
    date_str = [riga["Data"] for riga in dati if riga["Data"]]

    try:
        # Converto le stringhe in oggetti datetime
        date_ordinate = sorted(datetime.strptime(data, "%d/%m/%Y") for data in date_str)

        prima_data = date_ordinate[0]
        ultima_data = date_ordinate[-1]

        gg_totali = (ultima_data - prima_data).days

        return gg_totali

    except Exception as e:
        return 0

def calcola_gg_rimanenti():
    foglio_rif = client.open("Gestione auto").worksheet("Chilometraggio")
    dati = foglio_rif.get_all_records()

    if not dati:
        return 0

    try:
        # Estrai solo le date non vuote e convertile in datetime
        date_str = [r["Data"] for r in dati if r["Data"]]
        date_convertite = [datetime.strptime(data, "%d/%m/%Y") for data in date_str]
        ultima_data = max(date_convertite)

        # Sostituisci questa con la tua data ipotetica futura
        data_futura = datetime.strptime("30/05/2028", "%d/%m/%Y")

        gg_rimanenti = (data_futura - ultima_data).days

        return gg_rimanenti

    except Exception as e:
        return 0
    
def calcola_km_gg(km, gg_totali):
    km = int(km)  # o float(km) se prevedi virgole
    if gg_totali == 0:
        print("⚠️ Errore: giorni totali è 0, impossibile dividere.")
        return 0
    km_gg = km / gg_totali
    print(f"📊 KM totali: {km}, Giorni totali: {gg_totali}, KM/giorno: {km_gg:.2f}")
    return km_gg

def calcola_previsione_km(km_gg, gg_rimanenti):
    previsione_km = km_gg * gg_rimanenti
    print(f"📈 KM/giorno: {km_gg:.2f}, Giorni rimanenti: {gg_rimanenti}, Previsione KM: {previsione_km:.2f}")
    return previsione_km

def calcola_km_riconsegna(km, gg_totali, gg_rimanenti):
    km_gg = calcola_km_gg(km, gg_totali)
    previsione_km = calcola_previsione_km(km_gg, gg_rimanenti)
    km = int(km)  # oppure float(km), se usi decimali
    km_riconsegna = km + previsione_km
    print(f"🚗 KM attuali: {km}, KM previsti: {previsione_km:.2f}, KM alla riconsegna: {km_riconsegna:.2f}")
    return km_riconsegna