# -*- coding: utf-8 -*-
"""
GENERATORE EVENTI LIVE MANDRAKODI - VERSIONE FINALE
====================================================
Script per GitHub Actions
- Matching intelligente con campo language
- Raggruppamento per nazione (Italia prima)
- Ordinamento cronologico
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


# Mapping campionati → codici paese
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

# Emoji bandiere
COUNTRY_FLAGS = {
    'Italia': '🇮🇹', 'Inghilterra': 'eng', 'Spagna': '🇪🇸', 'Germania': '🇩🇪',
    'Francia': '🇫🇷', 'Europa': '🇪🇺', 'USA': '🇺🇸', 'Canada': '🇨🇦',
    'Portogallo': '🇵🇹', 'Olanda': '🇳🇱', 'Belgio': '🇧🇪', 'Turchia': '🇹🇷',
    'Svezia': '🇸🇪', 'Grecia': '🇬🇷', 'Repubblica Ceca': '🇨🇿',
    'Finlandia': '🇫🇮', 'Internazionale': '',
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
        print(f"📡 Download canali MandraKodi...")
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Errore HTTP: {response.status_code}")
            return []
        
        data = json.loads(response.text)
        
        channels = []
        for item in data.get('items', []):
            title = item.get('title', '')
            clean_name = re.sub(r'\[COLOR [^\]]+\]|\[/COLOR\]|\(ITA\)|\(ENG\)|\(ESP\)|\(FRA\)|\(UK\)|\(US\)|\(DE\)|\(CA\)', '', title).strip()
            
            # Estrai lingua da titolo
            language_match = re.search(r'\(([A-Z]{2,3})\)', title)
            language = language_match.group(1).lower() if language_match else None
            
            channels.append({
                'name': clean_name,
                'original_title': title,
                'thumbnail': item.get('thumbnail', ''),
                'stream': item.get('myresolve', ''),
                'fanart': item.get('fanart', 'https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg'),
                'info': item.get('info', ''),
                'language': item.get('language', language)
            })
        
        print(f"✓ Caricati {len(channels)} canali")
        return channels
    
    except Exception as e:
        print(f"❌ Errore: {e}")
        return []


def fetch_sports_events(url=SUPERLEAGUE_URL):
    """Scarica eventi da super.league.do"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        print(f"📡 Download eventi sportivi...")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Errore HTTP: {response.status_code}")
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
                print(f"✓ Trovati {len(matches)} eventi")
                break
        
        # Pattern VECCHIO (fallback)
        if not matches:
            old_pattern = r'"matches"\s*\:\s*(\[.+?])}]]}]n'
            for script in scripts:
                old_matches = re.findall(old_pattern, script.replace(',false', ''), re.DOTALL)
                if old_matches:
                    matches = json.loads(old_matches[0])
                    print(f"✓ Trovati {len(matches)} eventi")
                    break
        
        return matches
    
    except Exception as e:
        print(f"❌ Errore: {e}")
        return []


def normalize_name(name):
    """Normalizza nome per matching"""
    return name.lower().replace(' ', '').replace('-', '').replace('_', '')


def find_channel_advanced(channel_info, league, mandrakodi_channels):
    """
    Matching avanzato a 3 livelli:
    LIVELLO 1: Language code (priorità massima)
    LIVELLO 2: Nome con country suffix
    LIVELLO 3: Fuzzy matching normale
    """
    
    if isinstance(channel_info, str):
        channel_name = channel_info
        channel_language = None
    elif isinstance(channel_info, dict):
        channel_name = channel_info.get('name', '')
        channel_language = channel_info.get('language', None)
    else:
        return None
    
    if not channel_name:
        return None
    
    # ========================================================================
    # LIVELLO 1: Match per LANGUAGE CODE
    # ========================================================================
    if channel_language:
        lang_lower = channel_language.lower()
        
        for mk_ch in mandrakodi_channels:
            mk_lang = mk_ch.get('language', '').lower() if mk_ch.get('language') else None
            
            if mk_lang and mk_lang == lang_lower:
                if normalize_name(channel_name) in normalize_name(mk_ch['name']) or \
                   normalize_name(mk_ch['name']) in normalize_name(channel_name):
                    print(f"    ✓ Match LANGUAGE: {channel_name} ({channel_language}) → {mk_ch['name']}")
                    return mk_ch
    
    # ========================================================================
    # LIVELLO 2: Inferisci country da league
    # ========================================================================
    country_code = get_country_code_from_league(league)
    
    if country_code:
        search_variations = [
            f"{channel_name} {country_code.upper()}",
            f"{channel_name} ({country_code.upper()})",
        ]
        
        for search_var in search_variations:
            search_norm = normalize_name(search_var)
            
            for mk_ch in mandrakodi_channels:
                if search_norm in normalize_name(mk_ch['name']) or \
                   normalize_name(mk_ch['name']) in search_norm:
                    print(f"    ✓ Match COUNTRY: {channel_name} → {mk_ch['name']}")
                    return mk_ch
    
    # ========================================================================
    # LIVELLO 3: Fuzzy matching normale
    # ========================================================================
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


def generate_grouped_json(events, mandrakodi_channels):
    """Genera JSON raggruppato per nazione"""
    
    countries_dict = {}
    total_channels = 0
    events_processed = 0
    
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
        
        event_title = f'{team1} vs {team2}' if team1 and team2 else (team1 or 'Live Event')
        event_channels = match.get('channels', [])
        
        channels_found = []
        
        for ch in event_channels:
            mk_ch = find_channel_advanced(ch, league, mandrakodi_channels)
            
            if mk_ch and mk_ch['stream']:
                channels_found.append(mk_ch)
        
        if channels_found:
            events_processed += 1
            
            if country not in countries_dict:
                countries_dict[country] = []
            
            for mk_ch in channels_found:
                title = f"[COLOR cyan][{time_str}][/COLOR] "
                title += f"[COLOR gold]{event_title}[/COLOR] - "
                title += f"{mk_ch['original_title']}"
                
                info = f"{full_datetime} - {league}"
                
                channel_item = {
                    "title": title,
                    "myresolve": mk_ch['stream'],
                    "thumbnail": mk_ch['thumbnail'],
                    "fanart": mk_ch['fanart'],
                    "info": info,
                    "_timestamp": sort_timestamp
                }
                
                countries_dict[country].append(channel_item)
                total_channels += 1
    
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
        flag = COUNTRY_FLAGS.get(country, '🌍')
        separator = {
            "title": f"[B][COLOR yellow]═══ {flag} {country.upper()} ═══[/COLOR][/B]",
            "link": "ignoreme",
            "thumbnail": "https://cdn-icons-png.flaticon.com/512/814/814346.png",
            "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg",
            "info": f"Eventi {country}"
        }
        final_json['items'].append(separator)
        
        for item in countries_dict[country]:
            del item['_timestamp']
            final_json['items'].append(item)
    
    print(f"\n📊 STATISTICHE:")
    print(f"  ✓ Eventi processati: {events_processed}")
    print(f"  ✓ Canali totali: {total_channels}")
    print(f"  ✓ Nazioni: {len(countries_dict)}")
    
    return final_json


def save_json(json_data, filename='outputs/EVENTI_LIVE.json'):
    """Salva JSON"""
    import os
    os.makedirs('outputs', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ File salvato: {filename}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "GENERATORE EVENTI LIVE - VERSIONE FINALE" + " "*23 + "║")
    print("╚" + "="*78 + "╝\n")
    
    # 1. Canali
    print("STEP 1: Download canali MandraKodi")
    print("-" * 80)
    mandrakodi_channels = download_mandrakodi_channels()
    
    if not mandrakodi_channels:
        print("\n❌ IMPOSSIBILE CONTINUARE!")
        exit(1)
    
    # 2. Eventi
    print("\nSTEP 2: Download eventi sportivi")
    print("-" * 80)
    events = fetch_sports_events()
    
    if not events:
        print("\n❌ Nessun evento trovato!")
        exit(1)
    
    # 3. Matching
    print("\nSTEP 3: Matching avanzato (LANGUAGE + COUNTRY + FUZZY)")
    print("-" * 80)
    json_data = generate_grouped_json(events, mandrakodi_channels)
    
    if not json_data['items']:
        print("\n⚠ Nessun canale disponibile!")
        exit(1)
    
    # 4. Salva
    print("\nSTEP 4: Salvataggio")
    print("-" * 80)
    save_json(json_data)
    
    print("\n" + "="*80)
    print("✅ COMPLETATO!")
    print("="*80)
    print("\n💡 FEATURES:")
    print("  ✓ Matching intelligente con campo language")
    print("  ✓ Fallback su inferenza country da league")
    print("  ✓ Raggruppamento per nazione (Italia prima)")
    print("  ✓ Ordinamento cronologico")
    print("  ✓ Funziona per TUTTE le nazioni!")
