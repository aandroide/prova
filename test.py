# -*- coding: utf-8 -*-
"""
GENERATORE EVENTI LIVE MANDRAKODI - VERSIONE CARTELLE REALI
============================================================
- Crea cartelle per le 14 nazioni reali usate in super.league.do
- Un JSON principale + JSON per ogni nazione
- Matching esatto per thumbnail
"""

import requests
import json
import re
from datetime import datetime, timedelta
import os


# ============================================================================
# CONFIGURAZIONE - IMPORTANTE!
# ============================================================================

# CAMBIA QUESTO CON IL TUO USERNAME GITHUB!
GITHUB_USERNAME = 'aandroide'  # <-- MODIFICA QUI

MANDRAKODI_CANALI_URL = 'https://raw.githubusercontent.com/{}/prova/main/canali/canali.json'.format(GITHUB_USERNAME)
SUPERLEAGUE_URL = 'https://super.league.do'
GITHUB_RAW_BASE = 'https://raw.githubusercontent.com/{}/prova/main/outputs'.format(GITHUB_USERNAME)


# MAPPING NAZIONI REALI da super.league.do (basato sui codici lingua)
# Queste sono le 14 nazioni effettivamente presenti nel tuo HTML
COUNTRIES_REAL = {
    'AU': {'name': 'AUSTRALIA', 'code': 'au'},
    'CA': {'name': 'CANADA', 'code': 'ca'},
    'CZ': {'name': 'CECHIA', 'code': 'cz'},
    'DE': {'name': 'GERMANY', 'code': 'de'},
    'ES': {'name': 'SPAIN', 'code': 'es'},
    'FI': {'name': 'FINLAND', 'code': 'fi'},
    'FR': {'name': 'FRANCE', 'code': 'fr'},
    'GB': {'name': 'UNITED KINGDOM', 'code': 'gb'},
    'IT': {'name': 'ITALY', 'code': 'it'},
    'NO': {'name': 'NORWAY', 'code': 'no'},
    'PL': {'name': 'POLAND', 'code': 'pl'},
    'PT': {'name': 'PORTUGAL', 'code': 'pt'},
    'SE': {'name': 'SWEDEN', 'code': 'se'},
    'US': {'name': 'USA', 'code': 'us'}
}

# Mapping campionati -> codici paese (basato sulle nazioni reali)
LEAGUE_TO_COUNTRY = {
    # Italia
    'italy': 'IT', 'serie a': 'IT', 'serie b': 'IT', 'coppa italia': 'IT',
    # Inghilterra/UK
    'england': 'GB', 'premier league': 'GB', 'championship': 'GB', 
    'fa cup': 'GB', 'efl cup': 'GB', 'united kingdom': 'GB', 'scotland': 'GB',
    # Spagna
    'spain': 'ES', 'laliga': 'ES', 'la liga': 'ES', 'copa del rey': 'ES',
    # Germania
    'germany': 'DE', 'bundesliga': 'DE',
    # Francia
    'france': 'FR', 'ligue 1': 'FR', 'ligue 2': 'FR',
    # Portogallo
    'portugal': 'PT', 'primeira liga': 'PT',
    # Polonia
    'poland': 'PL',
    # Svezia
    'sweden': 'SE', 'allsvenskan': 'SE', 'shl': 'SE',
    # Finlandia
    'finland': 'FI', 'liiga': 'FI', 'mestis': 'FI',
    # Canada
    'canada': 'CA',
    # USA
    'usa': 'US', 'nba': 'US', 'nfl': 'US', 'nhl': 'US', 'mlb': 'US', 'mls': 'US',
    # Cechia
    'czech': 'CZ', 'cechia': 'CZ', 'czech republic': 'CZ',
    # Norvegia
    'norway': 'NO',
    # Australia
    'australia': 'AU',
    # Europa e Internazionale
    'champions league': 'EU', 'europa league': 'EU', 'conference league': 'EU', 
    'uefa': 'EU', 'euroleague': 'EU', 'eurocup': 'EU', 'world': 'INT', 'international': 'INT'
}

# Bandiere nazioni (URL delle bandiere circolari)
COUNTRY_FLAGS = {
    'IT': 'https://vectorflags.s3.amazonaws.com/flags/it-circle-01.png',
    'ES': 'https://vectorflags.s3.amazonaws.com/flags/es-sphere-01.png',
    'GB': 'https://vectorflags.s3.amazonaws.com/flags/uk-circle-01.png',
    'DE': 'https://vectorflags.s3.amazonaws.com/flags/de-circle-01.png',
    'FR': 'https://vectorflags.s3.amazonaws.com/flags/fr-circle-01.png',
    'PT': 'https://vectorflags.s3.amazonaws.com/flags/pt-circle-01.png',
    'US': 'https://vectorflags.s3.amazonaws.com/flags/us-circle-01.png',
    'CA': 'https://vectorflags.s3.amazonaws.com/flags/ca-circle-01.png',
    'SE': 'https://vectorflags.s3.amazonaws.com/flags/se-sphere-01.png',
    'FI': 'https://vectorflags.s3.amazonaws.com/flags/fi-circle-01.png',
    'PL': 'https://vectorflags.s3.amazonaws.com/flags/pl-circle-01.png',
    'CZ': 'https://vectorflags.s3.amazonaws.com/flags/cz-circle-01.png',
    'NO': 'https://vectorflags.s3.amazonaws.com/flags/no-circle-01.png',
    'AU': 'https://vectorflags.s3.amazonaws.com/flags/au-circle-01.png',
    'EU': 'https://vectorflags.s3.amazonaws.com/flags/org-eu-circle-01.png',
    'INT': 'https://vectorflags.s3.amazonaws.com/flags/org-eu-circle-01.png'
}


def get_country_code_from_league(league):
    """Estrae codice paese dal campionato"""
    if not league:
        return None
    
    league_lower = league.lower()
    for key, code in LEAGUE_TO_COUNTRY.items():
        if key in league_lower:
            return code
    return None


def get_country_from_channel_language(language_code):
    """Ottiene il paese dal codice lingua del canale"""
    if not language_code:
        return None
    
    lang_upper = language_code.upper()
    if lang_upper in COUNTRIES_REAL:
        return lang_upper
    
    # Fallback: mappature comuni
    lang_map = {
        'EN': 'GB', 'ENGLISH': 'GB', 'UK': 'GB',
        'GER': 'DE', 'GERMAN': 'DE',
        'FRA': 'FR', 'FRENCH': 'FR',
        'ESP': 'ES', 'SPANISH': 'ES',
        'ITA': 'IT', 'ITALIAN': 'IT',
        'POR': 'PT', 'PORTUGUESE': 'PT',
        'SWE': 'SE', 'SWEDISH': 'SE',
        'FIN': 'FI', 'FINNISH': 'FI',
        'POL': 'PL', 'POLISH': 'PL',
        'CZE': 'CZ', 'CZECH': 'CZ',
        'NOR': 'NO', 'NORWEGIAN': 'NO',
        'AUS': 'AU', 'AUSTRALIAN': 'AU'
    }
    
    return lang_map.get(lang_upper, None)


def download_mandrakodi_channels(url=MANDRAKODI_CANALI_URL):
    """Scarica canali MandraKodi da GitHub + info nazioni"""
    try:
        print("Download canali MandraKodi...")
        print("URL: {}".format(url))
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print("Errore HTTP: {}".format(response.status_code))
            print("Continuo senza thumbnail personalizzate")
            return [], {}  # Lista vuota + dizionario vuoto
        
        data = json.loads(response.text)
        
        # Supporta due formati:
        # Formato 1 (nested): {"channels": [{"name": "ITALY", "items": [...]}]}
        # Formato 2 (piatto): {"items": [{...}]}
        
        channels = []
        countries_info = {}
        
        # Formato NESTED (con gruppi per nazione)
        if 'channels' in data:
            # Estrai info nazioni (bandiere + nomi)
            for group in data.get('channels', []):
                name_raw = group.get('name', '')
                # Rimuovi tag COLOR
                name_clean = re.sub(r'\[COLOR [^\]]+\]|\[/COLOR\]', '', name_raw).strip()
                
                countries_info[name_clean.upper()] = {
                    'name': name_clean,
                    'thumbnail': group.get('thumbnail', ''),
                    'fanart': group.get('fanart', 'https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg')
                }
            
            # Estrai canali
            for group in data.get('channels', []):
                for item in group.get('items', []):
                    title = item.get('title', '')
                    clean_name = re.sub(r'\[COLOR [^\]]+\]|\[/COLOR\]|\(ITA\)|\(ENG\)|\(ESP\)|\(FRA\)|\(UK\)|\(US\)|\(DE\)|\(CA\)|\(AR\)|\(BR\)|\(PT\)|\(GR\)|\(PL\)|\(RS\)|\(CZ\)|\(HU\)|\(LT\)|\(NL\)|\(SWE\)|\(FRA\)|\(GER\)|\(AT\)|\(BE\)|\(UA\)|\(ENG\)', '', title).strip()
                    
                    channels.append({
                        'name': clean_name,
                        'thumbnail': item.get('thumbnail', ''),
                        'fanart': item.get('fanart', 'https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg'),
                    })
        
        # Formato PIATTO (lista diretta di canali)
        elif 'items' in data:
            for item in data.get('items', []):
                title = item.get('title', '')
                clean_name = re.sub(r'\[COLOR [^\]]+\]|\[/COLOR\]|\(ITA\)|\(ENG\)|\(ESP\)|\(FRA\)|\(UK\)|\(US\)|\(DE\)|\(CA\)|\(AR\)|\(BR\)|\(PT\)|\(GR\)|\(PL\)|\(RS\)|\(CZ\)|\(HU\)|\(LT\)|\(NL\)|\(SWE\)|\(FRA\)|\(GER\)|\(AT\)|\(BE\)|\(UA\)|\(ENG\)', '', title).strip()
                
                channels.append({
                    'name': clean_name,
                    'thumbnail': item.get('thumbnail', ''),
                    'fanart': item.get('fanart', 'https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg'),
                })
        
        
        print("Caricati {} canali per matching thumbnail".format(len(channels)))
        print("Caricati {} paesi con bandiere".format(len(countries_info)))
        return channels, countries_info
    
    except Exception as e:
        print("Errore download canali: {}".format(e))
        print("Continuo senza thumbnail personalizzate")
        return [], {}  # Lista vuota + dizionario vuoto


def extract_sansat_id(channel_info):
    """Estrae ID sansat dal link"""
    
    if isinstance(channel_info, dict):
        links = channel_info.get('links', [])
        
        if links and len(links) > 0:
            link = links[0]
            match = re.search(r'[?&]id=(\d+)', link)
            if match:
                return match.group(1)
    
    return None


def normalize_name(name):
    """Normalizza nome per matching"""
    return name.lower().replace(' ', '').replace('-', '').replace('_', '').replace('.', '')


def find_thumbnail(channel_name, mandrakodi_channels):
    """Cerca thumbnail con matching ESATTO"""
    
    if not mandrakodi_channels:
        return None
    
    search_norm = normalize_name(channel_name)
    
    # SOLO match ESATTO
    for mk_ch in mandrakodi_channels:
        # Verifica che sia un dizionario
        if not isinstance(mk_ch, dict):
            continue
        
        mk_name = mk_ch.get('name', '')
        if normalize_name(mk_name) == search_norm:
            return mk_ch
    
    return None


def fetch_sports_events(url=SUPERLEAGUE_URL):
    """Scarica eventi da super.league.do"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        print("Download eventi sportivi...")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print("Errore HTTP: {}".format(response.status_code))
            return []
        
        data = response.text
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', data, re.DOTALL)
        
        matches = []
        
        # Pattern NUOVO
        new_pattern = r'window\.matches\s*=\s*JSON\.parse\(`(\[.+?\])`\)'
        for script in scripts:
            new_matches = re.findall(new_pattern, script, re.DOTALL)
            if new_matches:
                matches = json.loads(new_matches[0])
                print("Trovati {} eventi".format(len(matches)))
                break
        
        # Pattern VECCHIO (fallback)
        if not matches:
            old_pattern = r'"matches"\s*\:\s*(\[.+?])}]]}]n'
            for script in scripts:
                old_matches = re.findall(old_pattern, script.replace(',false', ''), re.DOTALL)
                if old_matches:
                    matches = json.loads(old_matches[0])
                    print("Trovati {} eventi".format(len(matches)))
                    break
        
        return matches
    
    except Exception as e:
        print("Errore: {}".format(e))
        return []


def generate_country_jsons(events, mandrakodi_channels):
    """Genera JSON separati per ogni nazione REALE"""
    
    countries_dict = {}
    total_channels = 0
    events_processed = 0
    thumbnails_matched = 0
    
    for match in events:
        team1 = match.get('team1', '')
        team2 = match.get('team2', '')
        league = match.get('league', '')
        
        # Timestamp (+1 ora per timezone Italia)
        try:
            timestamp = match.get('startTimestamp', 0)
            if timestamp:
                start_time = datetime.fromtimestamp(timestamp / 1000) + timedelta(hours=1)
                time_str = start_time.strftime('%d/%m %H:%M')  # Data + orario
                full_datetime = start_time.strftime('%d-%b %H:%M')
                sort_timestamp = timestamp
            else:
                time_str = '?'
                full_datetime = 'Orario da definire'
                sort_timestamp = 9999999999999
        except:
            time_str = '?'
            full_datetime = 'Orario da definire'
            sort_timestamp = 9999999999999
        
        event_title = '{} vs {}'.format(team1, team2) if team1 and team2 else (team1 or 'Live Event')
        event_channels = match.get('channels', [])
        
        for ch in event_channels:
            channel_name = ch.get('name', '')
            channel_language = ch.get('language', '').upper()
            sansat_id = extract_sansat_id(ch)
            
            if sansat_id:
                # Determinare la nazione
                country_code = None
                
                # 1. Prima prova dal codice lingua del canale
                country_code = get_country_from_channel_language(channel_language)
                
                # 2. Fallback: dal campionato
                if not country_code:
                    country_code = get_country_code_from_league(league)
                
                # 3. Se ancora nessuno, usa 'OTHER'
                if not country_code:
                    country_code = 'OTHER'
                
                # Ottenere nome nazione per la cartella
                if country_code in COUNTRIES_REAL:
                    country_name = COUNTRIES_REAL[country_code]['name']
                elif country_code == 'EU':
                    country_name = 'EUROPA'
                elif country_code == 'INT':
                    country_name = 'INTERNAZIONALE'
                else:
                    country_name = 'OTHER'
                
                # Matching esatto per thumbnail
                mk_match = find_thumbnail(channel_name, mandrakodi_channels)
                
                if mk_match:
                    thumbnail = mk_match['thumbnail']
                    fanart = mk_match['fanart']
                    thumbnails_matched += 1
                else:
                    thumbnail = "https://cdn-icons-png.flaticon.com/512/3524/3524659.png"
                    fanart = "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
                
                if channel_language:
                    channel_display = "{} ({})".format(channel_name, channel_language)
                else:
                    channel_display = channel_name
                
                title = "[COLOR cyan][{}][/COLOR] ".format(time_str)
                title += "[COLOR gold]{}[/COLOR] - ".format(event_title)
                title += channel_display
                
                info = "{} - {}".format(full_datetime, league)
                
                channel_item = {
                    "title": title,
                    "myresolve": "sansat@@{}".format(sansat_id),
                    "thumbnail": thumbnail,
                    "fanart": fanart,
                    "info": info,
                    "_timestamp": sort_timestamp,
                    "_country_code": country_code
                }
                
                if country_name not in countries_dict:
                    countries_dict[country_name] = []
                
                countries_dict[country_name].append(channel_item)
                total_channels += 1
        
        if event_channels:
            events_processed += 1
    
    # Ordina eventi dentro ogni nazione
    for country in countries_dict:
        countries_dict[country].sort(key=lambda x: x['_timestamp'])
        # Rimuovi timestamp temporaneo
        for item in countries_dict[country]:
            del item['_timestamp']
            del item['_country_code']
    
    print("\nSTATISTICHE:")
    print("  Eventi processati: {}".format(events_processed))
    print("  Canali totali: {}".format(total_channels))
    print("  Nazioni: {}".format(len(countries_dict)))
    print("  Thumbnail matched: {}/{}".format(thumbnails_matched, total_channels))
    
    return countries_dict


def save_all_jsons(countries_dict, output_dir='outputs'):
    """Salva JSON principale + JSON per ogni nazione"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Ordina nazioni: Italia prima, poi alfabetico
    sorted_countries = []
    
    # Aggiungi le nazioni nell'ordine desiderato
    priority_countries = ['ITALY', 'UNITED KINGDOM', 'SPAIN', 'GERMANY', 'FRANCE', 
                         'USA', 'CANADA', 'PORTUGAL', 'SWEDEN', 'POLAND', 
                         'FINLAND', 'CECHIA', 'NORWAY', 'AUSTRALIA',
                         'EUROPA', 'INTERNAZIONALE', 'OTHER']
    
    for country in priority_countries:
        if country in countries_dict:
            sorted_countries.append(country)
    
    # Aggiungi eventuali altre nazioni non in lista
    other_countries = sorted([c for c in countries_dict.keys() 
                              if c not in priority_countries])
    sorted_countries.extend(other_countries)
    
    # 1. Salva JSON per ogni nazione
    print("\nSalvataggio JSON per nazione:")
    for country in sorted_countries:
        country_file = "EVENTI_{}.json".format(country.upper().replace(' ', '_'))
        country_path = os.path.join(output_dir, country_file)
        
        country_json = {
            "SetViewMode": "55",
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "items": countries_dict[country]
        }
        
        with open(country_path, 'w', encoding='utf-8') as f:
            json.dump(country_json, f, indent=2, ensure_ascii=False)
        
        print("  - {}".format(country_file))
    
    # 2. Crea JSON principale con cartelle
    main_json = {
        "SetViewMode": "55",
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "items": []
    }
    
    for country in sorted_countries:
        country_file = "EVENTI_{}.json".format(country.upper().replace(' ', '_'))
        country_url = "{}/{}".format(GITHUB_RAW_BASE, country_file)
        
        # Trova codice paese per ottenere la bandiera
        country_code = None
        for code, info in COUNTRIES_REAL.items():
            if info['name'] == country:
                country_code = code
                break
        
        # Se non trovato, cerca nei mapping speciali
        if not country_code:
            if country == 'EUROPA':
                country_code = 'EU'
            elif country == 'INTERNAZIONALE':
                country_code = 'INT'
            else:
                country_code = 'OTHER'
        
        folder_item = {
            "title": country,
            "externallink": country_url,
            "thumbnail": COUNTRY_FLAGS.get(country_code, "https://cdn-icons-png.flaticon.com/512/814/814346.png"),
            "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg",
            "info": "Eventi sportivi dalla {}".format(country)
        }
        
        main_json['items'].append(folder_item)
    
    main_path = os.path.join(output_dir, 'EVENTI_LIVE.json')
    with open(main_path, 'w', encoding='utf-8') as f:
        json.dump(main_json, f, indent=2, ensure_ascii=False)
    
    print("\nFile principale: EVENTI_LIVE.json")
    print("\nTotale file generati: {}".format(len(sorted_countries) + 1))
    
    # 3. Crea anche un file di riepilogo
    summary_path = os.path.join(output_dir, 'RIEPILOGO_NAZIONI.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("NAZIONI LIVE SUPER.LEAGUE.DO\n")
        f.write("=" * 40 + "\n\n")
        f.write("Ultimo aggiornamento: {}\n\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        for country in sorted_countries:
            count = len(countries_dict[country])
            f.write("{:20s}: {} canali\n".format(country, count))
    
    print("\nRiepilogo: RIEPILOGO_NAZIONI.txt")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("GENERATORE EVENTI LIVE - NAZIONI REALI SUPER.LEAGUE.DO")
    print("=" * 80)
    print()
    
    # Mostra le 14 nazioni reali
    print("NAZIONI REALI TROVATE IN SUPER.LEAGUE.DO:")
    print("-" * 40)
    for code, info in COUNTRIES_REAL.items():
        print("  {} ({})".format(info['name'], code))
    print()
    
    # 1. Canali
    print("STEP 1: Download canali MandraKodi (per thumbnail)")
    print("-" * 80)
    mandrakodi_channels, countries_info = download_mandrakodi_channels()
    
    # 2. Eventi
    print("\nSTEP 2: Download eventi sportivi")
    print("-" * 80)
    events = fetch_sports_events()
    
    if not events:
        print("\nNessun evento trovato!")
        exit(1)
    
    # 3. Genera dizionario per nazione
    print("\nSTEP 3: Organizzazione eventi per nazione")
    print("-" * 80)
    countries_dict = generate_country_jsons(events, mandrakodi_channels)
    
    if not countries_dict:
        print("\nNessun canale disponibile!")
        exit(1)
    
    # 4. Salva tutti i JSON
    print("\nSTEP 4: Salvataggio JSON")
    print("-" * 80)
    save_all_jsons(countries_dict)
    
    print("\n" + "=" * 80)
    print("COMPLETATO!")
    print("=" * 80)
    print("\nFEATURES:")
    print("  - 14 nazioni reali da super.league.do")
    print("  - Cartelle per nazione con bandiere")
    print("  - Un JSON per nazione")
    print("  - Matching esatto per thumbnail")
    print("  - sansat@@ID per myresolve")
