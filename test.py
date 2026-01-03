#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import re
import unicodedata
from datetime import datetime

def clean_text(text):
    """Rimuove accenti e caratteri speciali, rende tutto ASCII-safe"""
    if not text:
        return ""
    # Normalizza unicode e rimuove accenti
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_text = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    # Rimuove caratteri speciali mantenendo spazi e trattini
    clean = re.sub(r'[^A-Za-z0-9\s\-]', '', ascii_text)
    return clean.strip()

def parse_datetime(date_str, time_str):
    """Converte data e ora in stringa ISO - orari già corretti dal sito"""
    try:
        # Parsing data e ora (già in orario italiano dal sito)
        dt_str = f"{date_str} {time_str}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        
        # Ritorna ISO semplice - orari già corretti!
        return dt.strftime("%Y-%m-%dT%H:%M:00")
    except Exception as e:
        print(f"Errore parsing datetime: {e}")
        return None

def format_display_datetime(iso_datetime):
    """Formatta data e ora per il display nei titoli"""
    try:
        # Parse ISO datetime semplice (senza timezone)
        dt = datetime.strptime(iso_datetime, "%Y-%m-%dT%H:%M:%S")
        
        # Formato: Gio 16/01 - 20:45
        giorni = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom']
        giorno_settimana = giorni[dt.weekday()]
        return f"{giorno_settimana} {dt.strftime('%d/%m')} - {dt.strftime('%H:%M')}"
    except Exception as e:
        print(f"Errore format display: {e}")
        return ""

def scarica_eventi():
    """Scarica eventi live da super.league.do"""
    url = "https://super.league.do"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Errore scaricamento eventi: {e}")
        return None

def scarica_canali():
    """Scarica lista canali da GitHub"""
    url = "https://raw.githubusercontent.com/aandroide/prova/refs/heads/main/canali/canali.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Gestisci vari formati possibili
        if isinstance(data, list):
            # Formato: [{...}, {...}]
            return data
        elif isinstance(data, dict):
            # Formato: {"canali": [{...}]} o {"channels": [{...}]}
            if 'canali' in data:
                return data['canali']
            elif 'channels' in data:
                return data['channels']
            elif 'items' in data:
                return data['items']
            else:
                # Potrebbe essere un singolo oggetto
                return [data]
        else:
            return []
    except Exception as e:
        print(f"Errore scaricamento canali da GitHub: {e}")
        return []

def estrai_eventi(html_content):
    """Estrae eventi da HTML di super.league.do (JSON embedded)"""
    eventi = []
    
    try:
        # Estrai tutti gli script dalla pagina
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        
        matches = []
        
        # Pattern NUOVO: window.matches = JSON.parse(`[...]`)
        new_pattern = r'window\.matches\s*=\s*JSON\.parse\(`(\[.+?\])`\)'
        for script in scripts:
            new_matches = re.findall(new_pattern, script, re.DOTALL)
            if new_matches:
                matches = json.loads(new_matches[0])
                print(f"   ✓ Trovati {len(matches)} eventi (formato NUOVO)")
                break
        
        # Pattern VECCHIO: "matches": [...]
        if not matches:
            old_pattern = r'"matches"\s*:\s*(\[.+?\])'
            for script in scripts:
                old_matches = re.findall(old_pattern, script.replace(',false', ''), re.DOTALL)
                if old_matches:
                    matches = json.loads(old_matches[0])
                    print(f"   ✓ Trovati {len(matches)} eventi (formato VECCHIO)")
                    break
        
        # Estrai dati da ogni match
        for match in matches:
            team1 = match.get('team1', '')
            team2 = match.get('team2', '')
            league = match.get('league', '')
            sport = match.get('sport', 'Football')
            channels = match.get('channels', [])
            
            # Timestamp evento
            start_timestamp = match.get('startTimestamp', 0)
            if start_timestamp:
                # Converti da milliseconds a datetime
                dt = datetime.fromtimestamp(start_timestamp / 1000)
                date_str = dt.strftime('%Y-%m-%d')
                time_str = dt.strftime('%H:%M')
            else:
                # Fallback
                continue
            
            # Crea titolo evento
            if team1 and team2:
                title = f"{team1} vs {team2}"
            else:
                title = match.get('title', 'Evento')
            
            # Per ogni canale crea un evento
            for channel in channels:
                # Channel può essere stringa O oggetto {"name": "...", "language": "..."}
                if isinstance(channel, dict):
                    channel_name = channel.get('name', '')
                else:
                    channel_name = str(channel)
                
                if not channel_name:
                    continue
                
                iso_datetime = parse_datetime(date_str, time_str)
                if iso_datetime:
                    display_time = format_display_datetime(iso_datetime)
                    eventi.append({
                        'title': title,
                        'league': league,
                        'sport': sport,
                        'date': date_str,
                        'time': time_str,
                        'datetime': iso_datetime,
                        'display_time': display_time,
                        'channel': channel_name
                    })
    
    except Exception as e:
        print(f"   ❌ Errore estrazione eventi: {e}")
    
    return eventi

def match_canale(channel_name, canali_list):
    """Trova corrispondenza tra nome canale e lista canali con fuzzy matching aggressivo"""
    
    # Pulisci il nome del canale da super.league.do
    # Rimuovi suffissi tipo " - IT", " - UK", " - ES", ecc.
    channel_clean = channel_name
    channel_clean = re.sub(r'\s*-\s*[A-Z]{2}$', '', channel_clean)  # Rimuove " - IT"
    channel_clean = clean_text(channel_clean).lower().strip()
    
    # Prova match esatto
    for canale in canali_list:
        # canali.json può avere vari formati di nome
        canale_names = []
        
        # Aggiungi tutti i possibili nomi
        if isinstance(canale, dict):
            if 'name' in canale:
                canale_names.append(canale['name'])
            if 'title' in canale:
                canale_names.append(canale['title'])
            if 'channelName' in canale:
                canale_names.append(canale['channelName'])
        
        for canale_name in canale_names:
            canale_clean = clean_text(canale_name).lower().strip()
            
            # Match esatto
            if channel_clean == canale_clean:
                return canale
    
    # Prova match parziale (uno contiene l'altro)
    for canale in canali_list:
        canale_names = []
        if isinstance(canale, dict):
            if 'name' in canale:
                canale_names.append(canale['name'])
            if 'title' in canale:
                canale_names.append(canale['title'])
            if 'channelName' in canale:
                canale_names.append(canale['channelName'])
        
        for canale_name in canale_names:
            canale_clean = clean_text(canale_name).lower().strip()
            
            # Match parziale (uno contiene l'altro)
            if channel_clean in canale_clean or canale_clean in channel_clean:
                return canale
            
            # Match per parole (almeno 2 parole in comune)
            channel_words = set(channel_clean.split())
            canale_words = set(canale_clean.split())
            if len(channel_words) >= 2 and len(canale_words) >= 2:
                common = channel_words & canale_words
                if len(common) >= 2:
                    return canale
    
    return None

def genera_eventi_cartelle(eventi, canali):
    """Genera struttura JSON a cartelle per nazioni"""
    
    # Nomi nazioni (da canali.json)
    COUNTRY_NAMES = {
        'it': 'ITALY', 'ar': 'ARGENTINA', 'au': 'AUSTRALIA', 'at': 'AUSTRIA',
        'be': 'BELGIUM', 'br': 'BRASIL', 'ca': 'CANADA', 'cz': 'CECHIA',
        'fr': 'FRANCE', 'de': 'GERMANY', 'gr': 'GREECE', 'hu': 'HUNGARY',
        'lt': 'LITUANIA', 'nl': 'NEDERLAND', 'nz': 'NEW ZELAND', 'pl': 'POLAND',
        'pt': 'PORTUGAL', 'rs': 'SERBIA', 'es': 'SPAIN', 'se': 'SWEDEN',
        'ch': 'SWISS', 'kr': 'SOUTH COREA', 'ua': 'UKRAINA',
        'ae': 'UNITED ARAB EMIRATE', 'gb': 'UNITED KINDOM', 'us': 'USA',
        'other': 'OTHER', 'eu': 'EUROPA', 'int': 'INTERNAZIONALE',
    }
    
    # Bandiere nazioni (URL immagini PNG - da canali.json)
    COUNTRY_FLAGS = {
        'it': 'https://static.vecteezy.com/system/resources/previews/041/446/736/non_2x/italy-national-flag-free-png.png',
        'ar': 'https://vectorflags.s3.amazonaws.com/flags/ar-circle-01.png',
        'au': 'https://vectorflags.s3.amazonaws.com/flags/au-circle-01.png',
        'at': 'https://vectorflags.s3.amazonaws.com/flags/at-circle-01.png',
        'be': 'https://vectorflags.s3.amazonaws.com/flags/be-circle-01.png',
        'br': 'https://vectorflags.s3.amazonaws.com/flags/br-circle-01.png',
        'ca': 'https://vectorflags.s3.amazonaws.com/flags/ca-circle-01.png',
        'cz': 'https://vectorflags.s3.amazonaws.com/flags/cz-circle-01.png',
        'fr': 'https://vectorflags.s3.amazonaws.com/flags/fr-circle-01.png',
        'de': 'https://vectorflags.s3.amazonaws.com/flags/de-circle-01.png',
        'gr': 'https://vectorflags.s3.amazonaws.com/flags/gr-circle-01.png',
        'hu': 'https://vectorflags.s3.amazonaws.com/flags/hu-circle-01.png',
        'lt': 'https://vectorflags.s3.amazonaws.com/flags/lt-circle-01.png',
        'nl': 'https://vectorflags.s3.amazonaws.com/flags/nl-circle-01.png',
        'nz': 'https://vectorflags.s3.amazonaws.com/flags/nz-circle-01.png',
        'pl': 'https://vectorflags.s3.amazonaws.com/flags/pl-circle-01.png',
        'pt': 'https://vectorflags.s3.amazonaws.com/flags/pt-circle-01.png',
        'rs': 'https://vectorflags.s3.amazonaws.com/flags/rs-circle-01.png',
        'es': 'https://vectorflags.s3.amazonaws.com/flags/es-sphere-01.png',
        'se': 'https://vectorflags.s3.amazonaws.com/flags/se-sphere-01.png',
        'ch': 'https://vectorflags.s3.amazonaws.com/flags/ch-circle-01.png',
        'kr': 'https://vectorflags.s3.amazonaws.com/flags/kr-circle-01.png',
        'ua': 'https://vectorflags.s3.amazonaws.com/flags/ua-sphere-01.png',
        'ae': 'https://vectorflags.s3.amazonaws.com/flags/ae-circle-01.png',
        'gb': 'https://vectorflags.s3.amazonaws.com/flags/uk-circle-01.png',
        'us': 'https://vectorflags.s3.amazonaws.com/flags/us-circle-01.png',
        'other': 'https://vectorflags.s3.amazonaws.com/flags/org-eu-circle-01.png',
        'eu': 'https://vectorflags.s3.amazonaws.com/flags/org-eu-circle-01.png',
        'int': 'https://vectorflags.s3.amazonaws.com/flags/org-eu-circle-01.png',
    }
    
    # Struttura principale
    eventi_live = {
        "items": []
    }
    
    # Dizionario per raggruppare eventi per nazione
    eventi_per_nazione = {}
    
    for evento in eventi:
        canale_match = match_canale(evento['channel'], canali)
        
        if canale_match:
            # Prova vari campi per il country code
            country_code = None
            if 'country' in canale_match:
                country_code = canale_match['country']
            elif 'language' in canale_match:
                country_code = canale_match['language']
            elif 'lang' in canale_match:
                country_code = canale_match['lang']
            elif 'nation' in canale_match:
                country_code = canale_match['nation']
            
            if not country_code:
                country_code = 'other'
            
            country_code = country_code.lower()
            
            # Nome nazione uppercase (es: 'ITALY', 'UNITED KINDOM')
            nazione = COUNTRY_NAMES.get(country_code, 'OTHER')
            
            if nazione not in eventi_per_nazione:
                eventi_per_nazione[nazione] = []
            
            # Titolo con DATA e ORA
            title_display = f"{evento['display_time']} - {evento['title']}"
            
            # ID canale
            canale_id = canale_match.get('id') or canale_match.get('_id') or canale_match.get('channelId') or ''
            
            # Logo canale
            canale_logo = canale_match.get('logo') or canale_match.get('thumbnail') or canale_match.get('icon') or ''
            
            # Nome canale
            canale_nome = canale_match.get('name') or canale_match.get('title') or canale_match.get('channelName') or ''
            
            evento_item = {
                "title": title_display,
                "link": f"sansat@@{canale_id}",
                "thumbnail": canale_logo,
                "info": f"Data: {evento['display_time']}\n{evento['title']}\nCanale: {canale_nome}",
                "datetime": evento['datetime']
            }
            
            eventi_per_nazione[nazione].append(evento_item)
    
    # Genera cartelle nazioni in EVENTI_LIVE.json
    for country_code, country_name in COUNTRY_NAMES.items():
        if country_name in eventi_per_nazione and len(eventi_per_nazione[country_name]) > 0:
            flag_url = COUNTRY_FLAGS.get(country_code, COUNTRY_FLAGS['other'])
            eventi_live['items'].append({
                "title": country_name,
                "link": f"https://raw.githubusercontent.com/aandroide/prova/main/outputs/{country_name}.json",
                "thumbnail": flag_url,
                "info": f"Eventi live da {country_name}"
            })
    
    return eventi_live, eventi_per_nazione

def main():
    """Funzione principale"""
    print("=== MandraKodi Eventi Live Generator ===")
    print(f"Data/Ora corrente: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Orari dal sito sono GIÀ in timezone Italy (Europe/Rome)")
    print()
    
    # 1. Scarica eventi
    print("1. Scaricamento eventi da super.league.do...")
    html_eventi = scarica_eventi()
    if not html_eventi:
        print("ERRORE: Impossibile scaricare eventi")
        return {}
    
    # 2. Scarica canali
    print("2. Scaricamento canali...")
    canali = scarica_canali()
    print(f"   Caricati {len(canali)} canali")
    
    # 3. Estrai eventi
    print("3. Estrazione eventi...")
    eventi = estrai_eventi(html_eventi)
    print(f"   Trovati {len(eventi)} eventi")
    
    # 4. Genera struttura cartelle
    print("4. Generazione JSON cartelle...")
    eventi_live, eventi_per_nazione = genera_eventi_cartelle(eventi, canali)
    
    # Debug info
    total_match = sum(len(evts) for evts in eventi_per_nazione.values())
    match_rate = (total_match / len(eventi) * 100) if len(eventi) > 0 else 0
    print(f"   Match rate: {total_match}/{len(eventi)} ({match_rate:.1f}%)")
    if len(eventi_per_nazione) > 0:
        print(f"   Top 5 nazioni:")
        for nazione in sorted(eventi_per_nazione.keys(), key=lambda x: len(eventi_per_nazione[x]), reverse=True)[:5]:
            print(f"     - {nazione}: {len(eventi_per_nazione[nazione])} eventi")
    
    # 5. Salva file
    print("5. Salvataggio file JSON...")
    
    # File principale
    with open('EVENTI_LIVE.json', 'w', encoding='utf-8') as f:
        json.dump(eventi_live, f, ensure_ascii=True, indent=2)
    print("   - EVENTI_LIVE.json salvato")
    
    # File per nazione
    for nazione, eventi_naz in eventi_per_nazione.items():
        filename = f"{nazione}.json"
        nazione_json = {"items": eventi_naz}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(nazione_json, f, ensure_ascii=True, indent=2)
        print(f"   - {nazione}.json salvato ({len(eventi_naz)} eventi)")
    
    print()
    print("=== Generazione completata! ===")
    print(f"File principale: EVENTI_LIVE.json")
    print(f"Nazioni generate: {len(eventi_per_nazione)}")
    
    return {
        'eventi_live': eventi_live,
        'eventi_per_nazione': eventi_per_nazione
    }

if __name__ == "__main__":
    result = main()
