# -*- coding: utf-8 -*-
"""
GENERATORE EVENTI LIVE MANDRAKODI - VERSIONE CARTELLE
======================================================
- Crea cartelle per nazione invece di separatori
- Un JSON principale + JSON per ogni nazione
- Matching esatto per thumbnail
"""

import requests
import json
import re
from datetime import datetime
import os


# ============================================================================
# CONFIGURAZIONE - IMPORTANTE!
# ============================================================================

# CAMBIA QUESTO CON IL TUO USERNAME GITHUB!
GITHUB_USERNAME = 'aandroide'  # <-- MODIFICA QUI

MANDRAKODI_CANALI_URL = 'https://raw.githubusercontent.com/{}/prova/main/canali/canali.json'.format(GITHUB_USERNAME)'
SUPERLEAGUE_URL = 'https://super.league.do'
GITHUB_RAW_BASE = 'https://raw.githubusercontent.com/{}/prova/main/outputs'.format(GITHUB_USERNAME)'


# Mapping campionati -> codici paese
LEAGUE_TO_COUNTRY = {
    # Italia
    'italy': 'it', 'serie a': 'it', 'serie b': 'it', 'coppa italia': 'it',
    # Inghilterra
    'england': 'gb', 'premier league': 'gb', 'championship': 'gb', 
    'fa cup': 'gb', 'efl cup': 'gb', 'united kingdom': 'gb',
    # Spagna
    'spain': 'es', 'laliga': 'es', 'la liga': 'es', 'copa del rey': 'es',
    # Germania
    'germany': 'de', 'bundesliga': 'de',
    # Francia
    'france': 'fr', 'ligue 1': 'fr', 'ligue 2': 'fr',
    # Portogallo
    'portugal': 'pt', 'primeira liga': 'pt',
    # Olanda
    'netherlands': 'nl', 'eredivisie': 'nl', 'nederland': 'nl',
    # Belgio
    'belgium': 'be',
    # Brasile
    'brazil': 'br', 'brasil': 'br', 'brasileirao': 'br',
    # Argentina
    'argentina': 'ar',
    # Australia
    'australia': 'au',
    # Austria
    'austria': 'at',
    # Canada
    'canada': 'ca',
    # Cechia
    'czech': 'cz', 'cechia': 'cz', 'czech republic': 'cz',
    # Grecia
    'greece': 'gr',
    # Ungheria
    'hungary': 'hu',
    # Lituania
    'lithuania': 'lt', 'lituania': 'lt',
    # Nuova Zelanda
    'new zealand': 'nz',
    # Polonia
    'poland': 'pl',
    # Serbia
    'serbia': 'rs',
    # Svezia
    'sweden': 'se', 'allsvenskan': 'se', 'shl': 'se',
    # Svizzera
    'switzerland': 'ch', 'swiss': 'ch',
    # Corea
    'south korea': 'kr', 'korea': 'kr', 'corea': 'kr',
    # Ucraina
    'ukraine': 'ua', 'ukraina': 'ua',
    # Emirati Arabi
    'uae': 'ae', 'emirates': 'ae',
    # Turchia
    'turkey': 'tr',
    # Europa e Internazionale
    'champions league': 'eu', 'europa league': 'eu', 'conference league': 'eu', 
    'uefa': 'eu', 'euroleague': 'eu', 'eurocup': 'eu',
    # USA
    'nba': 'us', 'nfl': 'us', 'mlb': 'us', 'nhl': 'us', 'mls': 'us', 'usa': 'us',
    'finland': 'fi', 'scotland': 'gb', 'world': 'int',
}

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

# Bandiere nazioni (da canali.json)
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


def get_country_code_from_league(league):
    """Estrae codice paese dal campionato"""
    league_lower = league.lower()
    for key, code in LEAGUE_TO_COUNTRY.items():
        if key in league_lower:
            return code
    return None


def download_mandrakodi_channels(url=MANDRAKODI_CANALI_URL):
    """Scarica canali MandraKodi da GitHub + info nazioni"""
    try:
        print("Download canali MandraKodi...")
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print("Errore HTTP: {}".format(response.status_code))
            print("Continuo senza thumbnail personalizzate")
            return {}, {}
        
        data = json.loads(response.text)
        
        # Estrai info nazioni (bandiere + nomi)
        countries_info = {}
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
        channels = []
        for group in data.get('channels', []):
            for item in group.get('items', []):
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
        return {}, {}


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
    return name.lower().replace(' ', '').replace('-', '').replace('_', '')


def find_thumbnail(channel_name, mandrakodi_channels):
    """Cerca thumbnail con matching ESATTO"""
    
    if not mandrakodi_channels:
        return None
    
    search_norm = normalize_name(channel_name)
    
    # SOLO match ESATTO
    for mk_ch in mandrakodi_channels:
        if normalize_name(mk_ch['name']) == search_norm:
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


def generate_country_jsons(events, mandrakodi_channels, countries_info):
    """Genera JSON separati per ogni nazione"""
    
    countries_dict = {}
    total_channels = 0
    events_processed = 0
    thumbnails_matched = 0
    
    for match in events:
        team1 = match.get('team1', '')
        team2 = match.get('team2', '')
        league = match.get('league', '')
        
        # Identifica nazione
        country_code = get_country_code_from_league(league)
        country = COUNTRY_NAMES.get(country_code, 'Altri') if country_code else 'Altri'
        
        # Timestamp
        try:
            timestamp = match.get('startTimestamp', 0)
            if timestamp:
                start_time = datetime.fromtimestamp(timestamp / 1000)
                time_str = start_time.strftime('%H:%M')
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
                    "_timestamp": sort_timestamp
                }
                
                if country not in countries_dict:
                    countries_dict[country] = []
                
                countries_dict[country].append(channel_item)
                total_channels += 1
        
        if event_channels:
            events_processed += 1
    
    # Ordina eventi dentro ogni nazione
    for country in countries_dict:
        countries_dict[country].sort(key=lambda x: x['_timestamp'])
        # Rimuovi timestamp temporaneo
        for item in countries_dict[country]:
            del item['_timestamp']
    
    print("\nSTATISTICHE:")
    print("  Eventi processati: {}".format(events_processed))
    print("  Canali totali: {}".format(total_channels))
    print("  Nazioni: {}".format(len(countries_dict)))
    print("  Thumbnail matched: {}/{}".format(thumbnails_matched, total_channels))
    
    return countries_dict


def save_all_jsons(countries_dict, output_dir='outputs'):
    """Salva JSON principale + JSON per ogni nazione"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Ordina nazioni: Italia prima
    sorted_countries = []
    if 'Italia' in countries_dict:
        sorted_countries.append('Italia')
    
    other_countries = sorted([c for c in countries_dict.keys() if c != 'Italia'])
    sorted_countries.extend(other_countries)
    
    # 1. Salva JSON per ogni nazione
    print("\nSalvataggio JSON per nazione:")
    for country in sorted_countries:
        country_file = "EVENTI_{}.json".format(country.upper().replace(' ', '_'))
        country_path = os.path.join(output_dir, country_file)
        
        country_json = {
            "SetViewMode": "55",
            "items": countries_dict[country]
        }
        
        with open(country_path, 'w', encoding='utf-8') as f:
            json.dump(country_json, f, indent=2, ensure_ascii=False)
        
        print("  - {}".format(country_file))
    
    # 2. Crea JSON principale con cartelle
    main_json = {
        "SetViewMode": "55",
        "items": []
    }
    
    for country in sorted_countries:
        country_file = "EVENTI_{}.json".format(country.upper().replace(' ', '_'))
        country_url = "{}/{}".format(GITHUB_RAW_BASE, country_file)
        
        # Trova codice paese per ottenere la bandiera
        country_code = None
        for code, name in COUNTRY_NAMES.items():
            if name == country:
                country_code = code
                break
        
        folder_item = {
            "title": country,
            "externallink": country_url,
            "thumbnail": COUNTRY_FLAGS.get(country_code, "https://cdn-icons-png.flaticon.com/512/814/814346.png"),
            "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg",
            "info": "Eventi {}".format(country)
        }
        
        main_json['items'].append(folder_item)
    
    main_path = os.path.join(output_dir, 'EVENTI_LIVE.json')
    with open(main_path, 'w', encoding='utf-8') as f:
        json.dump(main_json, f, indent=2, ensure_ascii=False)
    
    print("\nFile principale: EVENTI_LIVE.json")
    print("\nTotale file generati: {}".format(len(sorted_countries) + 1))


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("GENERATORE EVENTI LIVE - VERSIONE CARTELLE")
    print("=" * 80)
    print()
    
    # 1. Canali
    print("STEP 1: Download canali MandraKodi (per thumbnail)")
    print("-" * 80)
    mandrakodi_channels = download_mandrakodi_channels()
    
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
    print("  - Cartelle per nazione invece di separatori")
    print("  - Un JSON per nazione")
    print("  - Matching esatto per thumbnail")
    print("  - sansat@@ID per myresolve")
