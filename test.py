# -*- coding: utf-8 -*-
"""
GENERATORE EVENTI LIVE MANDRAKODI - CON TAG LANG E LINK1+LINK2
===============================================================
- Estrae tag "lang" dai parametri URL
- Supporta sia link1 che link2
- Crea canali separati per ogni link disponibile
"""

import requests
import json
import re
from datetime import datetime, timedelta
import os
from urllib.parse import urlparse, parse_qs

# ============================================================================
# CONFIGURAZIONE
# ============================================================================

GITHUB_USERNAME = 'aandroide'  # <-- MODIFICA QUESTO!
MANDRAKODI_CANALI_URL = f'https://raw.githubusercontent.com/{GITHUB_USERNAME}/prova/main/canali/canali.json'
SUPERLEAGUE_URL = 'https://super.league.do'
GITHUB_RAW_BASE = f'https://raw.githubusercontent.com/{GITHUB_USERNAME}/prova/main/outputs'

# Mapping campionati -> nazioni
LEAGUE_TO_COUNTRY = {
    'italy': 'IT', 'serie a': 'IT', 'serie b': 'IT', 'coppa italia': 'IT',
    'england': 'GB', 'premier league': 'GB', 'championship': 'GB', 'fa cup': 'GB',
    'spain': 'ES', 'laliga': 'ES', 'la liga': 'ES', 'copa del rey': 'ES',
    'germany': 'DE', 'bundesliga': 'DE',
    'france': 'FR', 'ligue 1': 'FR', 'ligue 2': 'FR',
    'portugal': 'PT', 'primeira liga': 'PT',
    'poland': 'PL',
    'sweden': 'SE', 'allsvenskan': 'SE', 'shl': 'SE',
    'finland': 'FI', 'liiga': 'FI', 'mestis': 'FI',
    'canada': 'CA',
    'usa': 'US', 'nba': 'US', 'nfl': 'US', 'nhl': 'US', 'mlb': 'US',
    'czech': 'CZ', 'czech republic': 'CZ',
    'norway': 'NO',
    'australia': 'AU',
    'champions league': 'EU', 'europa league': 'EU', 'uefa': 'EU',
    'world': 'INT', 'international': 'INT', 'africa cup of nations': 'AFR'
}

# Nomi nazioni
COUNTRY_NAMES = {
    'IT': 'ITALY', 'GB': 'UNITED KINGDOM', 'ES': 'SPAIN', 'DE': 'GERMANY',
    'FR': 'FRANCE', 'PT': 'PORTUGAL', 'US': 'USA', 'CA': 'CANADA',
    'SE': 'SWEDEN', 'FI': 'FINLAND', 'PL': 'POLAND', 'CZ': 'CECHIA',
    'NO': 'NORWAY', 'AU': 'AUSTRALIA', 'EU': 'EUROPA', 'INT': 'INTERNAZIONALE',
    'AFR': 'AFRICA'
}

# Bandiere
COUNTRY_FLAGS = {
    'IT': 'https://vectorflags.s3.amazonaws.com/flags/it-circle-01.png',
    'GB': 'https://vectorflags.s3.amazonaws.com/flags/uk-circle-01.png',
    'ES': 'https://vectorflags.s3.amazonaws.com/flags/es-sphere-01.png',
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
    'INT': 'https://vectorflags.s3.amazonaws.com/flags/org-eu-circle-01.png',
    'AFR': 'https://vectorflags.s3.amazonaws.com/flags/africa-circle-01.png'
}

def get_country_from_league(league):
    """Dove mettere l'evento (nazione del campionato)"""
    if not league:
        return 'INT'
    
    league_lower = league.lower()
    for key, code in LEAGUE_TO_COUNTRY.items():
        if key in league_lower:
            return code
    return 'INT'

def get_country_name_from_code(country_code):
    """Nome nazione dal codice"""
    return COUNTRY_NAMES.get(country_code, 'OTHER')

def get_country_from_language(lang):
    """Paese dalla lingua (per etichetta)"""
    if not lang:
        return None
    
    lang_upper = lang.upper()
    lang_map = {
        'EN': 'GB', 'GER': 'DE', 'FRA': 'FR', 'ESP': 'ES', 'ITA': 'IT',
        'POR': 'PT', 'SWE': 'SE', 'FIN': 'FI', 'POL': 'PL', 'CZE': 'CZ',
        'NOR': 'NO', 'AUS': 'AU', 'CA': 'CA', 'US': 'US'
    }
    return lang_map.get(lang_upper, None)

def extract_link_info(url):
    """
    Estrae ID e LANG dal link
    Supporta formati:
    - ?id=123&lang=it
    - ?id=123
    Ritorna: (id, lang) o (None, None)
    """
    if not url:
        return None, None
    
    try:
        # Parsing URL
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Estrai ID
        link_id = None
        if 'id' in params:
            link_id = params['id'][0]
        else:
            # Prova con regex fallback
            match = re.search(r'[?&]id=(\d+)', url)
            if match:
                link_id = match.group(1)
        
        # Estrai LANG
        link_lang = None
        if 'lang' in params:
            link_lang = params['lang'][0].upper()
        else:
            # Prova con regex fallback
            match = re.search(r'[?&]lang=([a-zA-Z]+)', url)
            if match:
                link_lang = match.group(1).upper()
        
        return link_id, link_lang
    
    except:
        return None, None

def extract_all_links(channel_info):
    """
    Estrae TUTTI i link disponibili da un canale
    Ritorna: [(id, lang, link_number), ...]
    """
    links_data = []
    
    if not isinstance(channel_info, dict):
        return links_data
    
    # Metodo 1: array 'links'
    links_array = channel_info.get('links', [])
    for idx, link in enumerate(links_array, 1):
        link_id, link_lang = extract_link_info(link)
        if link_id:
            links_data.append((link_id, link_lang, idx))
    
    # Metodo 2: campi separati link1, link2, ecc.
    link_num = 1
    while True:
        link_key = f'link{link_num}'
        if link_key in channel_info:
            link_url = channel_info[link_key]
            link_id, link_lang = extract_link_info(link_url)
            if link_id:
                links_data.append((link_id, link_lang, link_num))
            link_num += 1
        else:
            break
    
    return links_data

def download_mandrakodi_channels():
    """Scarica canali per thumbnail"""
    try:
        print("Scarico canali MandraKodi...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(MANDRAKODI_CANALI_URL, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print("Errore HTTP:", response.status_code)
            return [], {}
        
        data = json.loads(response.text)
        channels = []
        
        # Supporta entrambi i formati
        if 'channels' in data:
            for group in data.get('channels', []):
                for item in group.get('items', []):
                    title = item.get('title', '')
                    clean_name = re.sub(r'\[COLOR [^\]]+\]|\[/COLOR\]|\([A-Z]+\)', '', title).strip()
                    channels.append({
                        'name': clean_name,
                        'thumbnail': item.get('thumbnail', ''),
                        'fanart': item.get('fanart', 'https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg'),
                    })
        elif 'items' in data:
            for item in data.get('items', []):
                title = item.get('title', '')
                clean_name = re.sub(r'\[COLOR [^\]]+\]|\[/COLOR\]|\([A-Z]+\)', '', title).strip()
                channels.append({
                    'name': clean_name,
                    'thumbnail': item.get('thumbnail', ''),
                    'fanart': item.get('fanart', 'https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg'),
                })
        
        print(f"Caricati {len(channels)} canali per thumbnail")
        return channels, {}
    
    except Exception as e:
        print("Errore:", e)
        return [], {}

def normalize_name(name):
    """Per matching thumbnail"""
    return name.lower().replace(' ', '').replace('-', '').replace('_', '').replace('.', '')

def find_thumbnail(channel_name, mandrakodi_channels):
    """Cerca thumbnail esatta"""
    if not mandrakodi_channels:
        return None
    
    search_norm = normalize_name(channel_name)
    for mk_ch in mandrakodi_channels:
        if isinstance(mk_ch, dict):
            mk_name = mk_ch.get('name', '')
            if normalize_name(mk_name) == search_norm:
                return mk_ch
    return None

def fetch_sports_events():
    """Scarica eventi da super.league.do"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        print("Scarico eventi sportivi...")
        response = requests.get(SUPERLEAGUE_URL, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print("Errore HTTP:", response.status_code)
            return []
        
        data = response.text
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', data, re.DOTALL)
        
        for script in scripts:
            new_pattern = r'window\.matches\s*=\s*JSON\.parse\(`(\[.+?\])`\)'
            new_matches = re.findall(new_pattern, script, re.DOTALL)
            if new_matches:
                matches = json.loads(new_matches[0])
                print(f"Trovati {len(matches)} eventi")
                return matches
        
        return []
    
    except Exception as e:
        print("Errore:", e)
        return []

def generate_country_jsons(events, mandrakodi_channels):
    """
    Crea JSON per ogni nazione
    NOVITA: Estrae TUTTI i link (link1, link2, ecc.) e aggiunge tag lang
    """
    
    countries_dict = {}
    total_channels = 0
    total_links = 0
    thumbnails_matched = 0
    lang_found = 0
    
    for match in events:
        team1 = match.get('team1', '')
        team2 = match.get('team2', '')
        league = match.get('league', '')
        sport = match.get('sport', 'Football')
        
        # Orario
        try:
            timestamp = match.get('startTimestamp', 0)
            if timestamp:
                start_time = datetime.fromtimestamp(timestamp / 1000) + timedelta(hours=1)
                time_str = start_time.strftime('%d/%m %H:%M')
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
        
        event_title = f'{team1} vs {team2}' if team1 and team2 else (team1 or 'Live Event')
        event_channels = match.get('channels', [])
        
        # Nazione dell'evento (dal campionato)
        event_country_code = get_country_from_league(league)
        event_country_name = get_country_name_from_code(event_country_code)
        
        # Per ogni canale
        for ch in event_channels:
            total_channels += 1
            channel_name = ch.get('name', '')
            channel_language = ch.get('language', '').upper()
            
            # Estrai TUTTI i link disponibili
            all_links = extract_all_links(ch)
            
            if not all_links:
                # Nessun link valido, salta
                continue
            
            # Crea un item per OGNI link
            for link_id, link_lang, link_number in all_links:
                total_links += 1
                
                # Usa lang dal link se disponibile, altrimenti dal canale
                final_lang = link_lang if link_lang else channel_language
                if link_lang:
                    lang_found += 1
                
                # Paese del canale (per etichetta)
                channel_country_code = get_country_from_language(final_lang)
                channel_country_flag = f'[{channel_country_code}]' if channel_country_code else ''
                
                # Thumbnail
                mk_match = find_thumbnail(channel_name, mandrakodi_channels)
                if mk_match:
                    thumbnail = mk_match['thumbnail']
                    fanart = mk_match['fanart']
                    thumbnails_matched += 1
                else:
                    thumbnail = "https://cdn-icons-png.flaticon.com/512/3524/3524659.png"
                    fanart = "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
                
                # Titolo: [CANALE lang] in CYAN + Link X
                # Se un solo link: [CANALE lang] (senza Link 1)
                
                # Costruisci parte canale [NOME lang] in CYAN
                if final_lang:
                    channel_part = f"[COLOR cyan][{channel_name} {final_lang.lower()}][/COLOR]"
                else:
                    channel_part = channel_name
                
                # Aggiungi "Link X" se necessario
                if len(all_links) == 1:
                    # Un solo link - no indicatore
                    channel_display = channel_part
                else:
                    # Multipli link
                    channel_display = f"{channel_part} Link {link_number}"
                
                title = f"[COLOR cyan][{time_str}][/COLOR] "
                title += f"[COLOR gold]{event_title}[/COLOR] - "
                title += channel_display
                
                # Info con tag lang se disponibile
                info_parts = [full_datetime, league, sport]
                if final_lang:
                    info_parts.append(f"Lang: {final_lang}")
                info = " | ".join(info_parts)
                
                # MyResolve con tag lang se disponibile
                if final_lang:
                    myresolve = f"sansat@@{link_id}@@{final_lang}"
                else:
                    myresolve = f"sansat@@{link_id}"
                
                channel_item = {
                    "title": title,
                    "myresolve": myresolve,
                    "thumbnail": thumbnail,
                    "fanart": fanart,
                    "info": info,
                    "_timestamp": sort_timestamp
                }
                
                # Aggiungi alla nazione del CAMPIONATO
                if event_country_name not in countries_dict:
                    countries_dict[event_country_name] = []
                
                countries_dict[event_country_name].append(channel_item)
    
    # Ordina per data
    for country in countries_dict:
        countries_dict[country].sort(key=lambda x: x['_timestamp'])
        for item in countries_dict[country]:
            del item['_timestamp']
    
    print(f"\nSTATISTICHE:")
    print(f"  Eventi processati: {len(events)}")
    print(f"  Canali totali: {total_channels}")
    print(f"  Link totali estratti: {total_links}")
    print(f"  Tag lang trovati: {lang_found}/{total_links}")
    print(f"  Nazioni: {len(countries_dict)}")
    print(f"  Thumbnail trovate: {thumbnails_matched}/{total_links}")
    
    print("\nDISTRIBUZIONE:")
    for country in sorted(countries_dict.keys()):
        print(f"  {country:20s}: {len(countries_dict[country])} canali")
    
    return countries_dict

def save_all_jsons(countries_dict, output_dir='outputs'):
    """Salva tutti i file JSON"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Ordine cartelle
    priority_countries = ['ITALY', 'UNITED KINGDOM', 'SPAIN', 'GERMANY', 'FRANCE', 
                         'USA', 'CANADA', 'PORTUGAL', 'SWEDEN', 'POLAND', 
                         'FINLAND', 'CECHIA', 'NORWAY', 'AUSTRALIA',
                         'EUROPA', 'INTERNAZIONALE', 'AFRICA']
    
    sorted_countries = []
    for country in priority_countries:
        if country in countries_dict:
            sorted_countries.append(country)
    
    other_countries = sorted([c for c in countries_dict.keys() if c not in priority_countries])
    sorted_countries.extend(other_countries)
    
    # 1. JSON per ogni nazione
    print("\nSalvo JSON per nazione:")
    for country in sorted_countries:
        country_file = f"EVENTI_{country.replace(' ', '_')}.json"
        country_path = os.path.join(output_dir, country_file)
        
        country_json = {
            "SetViewMode": "55",
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "items": countries_dict[country]
        }
        
        with open(country_path, 'w', encoding='utf-8') as f:
            json.dump(country_json, f, indent=2, ensure_ascii=False)
        
        print(f"  - {country_file} ({len(countries_dict[country])} canali)")
    
    # 2. JSON principale
    main_json = {
        "SetViewMode": "55",
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "items": []
    }
    
    for country in sorted_countries:
        country_file = f"EVENTI_{country.replace(' ', '_')}.json"
        country_url = f"{GITHUB_RAW_BASE}/{country_file}"
        
        # Bandiera
        country_code = None
        for code, name in COUNTRY_NAMES.items():
            if name == country:
                country_code = code
                break
        
        channel_count = len(countries_dict[country])
        
        folder_item = {
            "title": f"{country} ({channel_count})",
            "externallink": country_url,
            "thumbnail": COUNTRY_FLAGS.get(country_code, "https://cdn-icons-png.flaticon.com/512/814/814346.png"),
            "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg",
            "info": f"{channel_count} canali {country}"
        }
        
        main_json['items'].append(folder_item)
    
    main_path = os.path.join(output_dir, 'EVENTI_LIVE.json')
    with open(main_path, 'w', encoding='utf-8') as f:
        json.dump(main_json, f, indent=2, ensure_ascii=False)
    
    print(f"\nFile principale: EVENTI_LIVE.json")
    print(f"Totale file: {len(sorted_countries) + 1}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("GENERATORE EVENTI LIVE - CON TAG LANG E LINK1+LINK2")
    print("=" * 80)
    print("[OK] Estrae tag lang dai parametri URL")
    print("[OK] Supporta link1, link2, link3, ecc.")
    print("[OK] Crea canali separati per ogni link")
    print()
    
    # 1. Canali
    print("STEP 1: Download canali MandraKodi")
    print("-" * 80)
    mandrakodi_channels, _ = download_mandrakodi_channels()
    
    # 2. Eventi
    print("\nSTEP 2: Download eventi sportivi")
    print("-" * 80)
    events = fetch_sports_events()
    
    if not events:
        print("Nessun evento trovato!")
        exit(1)
    
    # 3. Genera JSON
    print("\nSTEP 3: Organizzazione eventi")
    print("-" * 80)
    countries_dict = generate_country_jsons(events, mandrakodi_channels)
    
    if not countries_dict:
        print("Nessun canale disponibile!")
        exit(1)
    
    # 4. Salva
    print("\nSTEP 4: Salvataggio")
    print("-" * 80)
    save_all_jsons(countries_dict)
    
    print("\n" + "=" * 80)
    print("COMPLETATO!")
    print("=" * 80)
    print("\nESEMPIO OUTPUT:")
    print("  myresolve: 'sansat@@12345@@IT'")
    print("  myresolve: 'sansat@@67890@@EN'")
    print("  myresolve: 'sansat@@11111'  (senza lang)")
    print("\nSE UN CANALE HA 2 LINK:")
    print('  - [COLOR cyan][DAZN1 it][/COLOR] Link 1')
    print('  - [COLOR cyan][DAZN1 en][/COLOR] Link 2')
