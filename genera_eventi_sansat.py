# -*- coding: utf-8 -*-
"""
GENERATORE EVENTI LIVE MANDRAKODI - VERSIONE SANSAT IBRIDA
===========================================================
"""

import requests
import json
import re
from datetime import datetime


# ============================================================================
# CONFIGURAZIONE
# ============================================================================

MANDRAKODI_CANALI_URL = 'https://raw.githubusercontent.com/aandroide/prova/main/canali/canali.json'
SUPERLEAGUE_URL = 'https://super.league.do'


# Mapping campionati -> codici paese
LEAGUE_TO_COUNTRY = {
    'italy': 'it', 'serie a': 'it', 'serie b': 'it', 'coppa italia': 'it',
    'england': 'gb', 'premier league': 'gb', 'championship': 'gb', 'fa cup': 'gb', 'efl cup': 'gb',
    'spain': 'es', 'laliga': 'es', 'la liga': 'es', 'copa del rey': 'es',
    'germany': 'de', 'bundesliga': 'de',
    'france': 'fr', 'ligue 1': 'fr', 'ligue 2': 'fr',
    'portugal': 'pt', 'primeira liga': 'pt',
    'netherlands': 'nl', 'eredivisie': 'nl',
    'belgium': 'be',
    'champions league': 'eu', 'europa league': 'eu', 'conference league': 'eu', 
    'uefa': 'eu', 'euroleague': 'eu', 'eurocup': 'eu',
    'nba': 'us', 'nfl': 'us', 'mlb': 'us', 'nhl': 'us', 'mls': 'us',
    'cfl': 'ca',
    'sweden': 'se', 'allsvenskan': 'se', 'shl': 'se',
    'turkey': 'tr', 'greece': 'gr', 'scotland': 'gb', 
    'czech republic': 'cz', 'finland': 'fi', 'world': 'int',
}

# Nomi completi nazioni
COUNTRY_NAMES = {
    'it': 'Italia', 'gb': 'Inghilterra', 'es': 'Spagna', 'de': 'Germania',
    'fr': 'Francia', 'eu': 'Europa', 'us': 'USA', 'ca': 'Canada',
    'pt': 'Portogallo', 'nl': 'Olanda', 'be': 'Belgio', 'tr': 'Turchia',
    'se': 'Svezia', 'gr': 'Grecia', 'cz': 'Repubblica Ceca', 
    'fi': 'Finlandia', 'int': 'Internazionale',
}


def get_country_code_from_league(league):
    """Estrae codice paese dal campionato"""
    league_lower = league.lower()
    for key, code in LEAGUE_TO_COUNTRY.items():
        if key in league_lower:
            return code
    return None


def download_mandrakodi_channels(url=MANDRAKODI_CANALI_URL):
    """Scarica canali MandraKodi da GitHub"""
    try:
        print("Download canali MandraKodi...")
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print("Errore HTTP: {}".format(response.status_code))
            print("Continuo senza thumbnail personalizzate")
            return []
        
        data = json.loads(response.text)
        
        channels = []
        for item in data.get('items', []):
            title = item.get('title', '')
            clean_name = re.sub(r'\[COLOR [^\]]+\]|\[/COLOR\]|\(ITA\)|\(ENG\)|\(ESP\)|\(FRA\)|\(UK\)|\(US\)|\(DE\)|\(CA\)', '', title).strip()
            
            channels.append({
                'name': clean_name,
                'thumbnail': item.get('thumbnail', ''),
                'fanart': item.get('fanart', 'https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg'),
            })
        
        print("Caricati {} canali per matching thumbnail".format(len(channels)))
        return channels
    
    except Exception as e:
        print("Errore download canali: {}".format(e))
        print("Continuo senza thumbnail personalizzate")
        return []


def extract_sansat_id(channel_info):
    """
    Estrae ID sansat dal link
    
    Input: {"links": ["https://sansat.link/ch?id=17"]}
    Output: "17"
    """
    
    if isinstance(channel_info, dict):
        links = channel_info.get('links', [])
        
        if links and len(links) > 0:
            link = links[0]
            
            # Pattern: sansat.link/ch?id=NUMERO
            match = re.search(r'[?&]id=(\d+)', link)
            if match:
                return match.group(1)
    
    return None


def normalize_name(name):
    """Normalizza nome per matching"""
    return name.lower().replace(' ', '').replace('-', '').replace('_', '')


def find_thumbnail(channel_name, mandrakodi_channels):
    """
    Cerca thumbnail nel JSON MandraKodi tramite matching fuzzy
    """
    
    if not mandrakodi_channels:
        return None
    
    search_norm = normalize_name(channel_name)
    
    # Match diretto
    for mk_ch in mandrakodi_channels:
        if normalize_name(mk_ch['name']) == search_norm:
            return mk_ch
    
    # Match parziale
    for mk_ch in mandrakodi_channels:
        mk_norm = normalize_name(mk_ch['name'])
        if search_norm in mk_norm or mk_norm in search_norm:
            return mk_ch
    
    # Match keyword
    keywords = [k for k in channel_name.lower().split() if len(k) > 3]
    for keyword in keywords:
        for mk_ch in mandrakodi_channels:
            if keyword in normalize_name(mk_ch['name']):
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


def generate_grouped_json(events, mandrakodi_channels):
    """Genera JSON raggruppato per nazione usando link sansat + thumbnail da canali.json"""
    
    countries_dict = {}
    total_channels = 0
    events_processed = 0
    thumbnails_matched = 0
    
    for match in events:
        team1 = match.get('team1', '')
        team2 = match.get('team2', '')
        league = match.get('league', '')
        sport = match.get('sport', '')
        
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
        
        channels_found = []
        
        for ch in event_channels:
            # Estrai info canale
            channel_name = ch.get('name', '')
            channel_language = ch.get('language', '').upper()
            sansat_id = extract_sansat_id(ch)
            
            if sansat_id:
                # MATCHING IBRIDO: cerca thumbnail
                mk_match = find_thumbnail(channel_name, mandrakodi_channels)
                
                if mk_match:
                    thumbnail = mk_match['thumbnail']
                    fanart = mk_match['fanart']
                    thumbnails_matched += 1
                else:
                    # Fallback icona generica
                    thumbnail = "https://cdn-icons-png.flaticon.com/512/3524/3524659.png"
                    fanart = "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
                
                # Aggiungi language al nome se disponibile
                if channel_language:
                    channel_display = "{} ({})".format(channel_name, channel_language)
                else:
                    channel_display = channel_name
                
                # Titolo
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
                
                channels_found.append(channel_item)
                total_channels += 1
        
        if channels_found:
            events_processed += 1
            
            if country not in countries_dict:
                countries_dict[country] = []
            
            countries_dict[country].extend(channels_found)
    
    # Ordina items dentro ogni nazione
    for country in countries_dict:
        countries_dict[country].sort(key=lambda x: x['_timestamp'])
    
    # Ordina nazioni: Italia prima
    sorted_countries = []
    if 'Italia' in countries_dict:
        sorted_countries.append('Italia')
    
    other_countries = sorted([c for c in countries_dict.keys() if c != 'Italia'])
    sorted_countries.extend(other_countries)
    
    # Crea JSON finale
    final_json = {"SetViewMode": "55", "items": []}
    
    for country in sorted_countries:
        # Separatore nazione
        separator = {
            "title": "[B][COLOR yellow]=== {} ===[/COLOR][/B]".format(country.upper()),
            "link": "ignoreme",
            "thumbnail": "https://cdn-icons-png.flaticon.com/512/814/814346.png",
            "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg",
            "info": "Eventi {}".format(country)
        }
        final_json['items'].append(separator)
        
        # Items della nazione
        for item in countries_dict[country]:
            del item['_timestamp']
            final_json['items'].append(item)
    
    print("\nSTATISTICHE:")
    print("  Eventi processati: {}".format(events_processed))
    print("  Canali totali: {}".format(total_channels))
    print("  Nazioni: {}".format(len(countries_dict)))
    print("  Thumbnail matched: {}/{}".format(thumbnails_matched, total_channels))
    
    return final_json


def save_json(json_data, filename='outputs/EVENTI_LIVE.json'):
    """Salva JSON"""
    import os
    os.makedirs('outputs', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print("\nFile salvato: {}".format(filename))


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("GENERATORE EVENTI LIVE - VERSIONE SANSAT IBRIDA")
    print("=" * 80)
    print()
    
    # 1. Canali (per thumbnail)
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
    
    # 3. Genera JSON con link sansat + thumbnail
    print("\nSTEP 3: Generazione eventi (sansat@@ID + thumbnail)")
    print("-" * 80)
    json_data = generate_grouped_json(events, mandrakodi_channels)
    
    if not json_data['items']:
        print("\nNessun canale disponibile!")
        exit(1)
    
    # 4. Salva
    print("\nSTEP 4: Salvataggio")
    print("-" * 80)
    save_json(json_data)
    
    print("\n" + "=" * 80)
    print("COMPLETATO!")
    print("=" * 80)
    print("\nFEATURES:")
    print("  - Usa sansat@@ID per myresolve")
    print("  - Matching con canali.json per thumbnail")
    print("  - Fallback icona generica se non trova match")
    print("  - Raggruppamento per nazione (Italia prima)")
    print("  - Ordinamento cronologico")
