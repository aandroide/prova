# -*- coding: utf-8 -*-
"""
GENERATORE EVENTI LIVE MANDRAKODI - VERSIONE SANSAT
====================================================
Usa direttamente link sansat@@ da super.league.do
- NO matching necessario
- Genera eventi per TUTTI i canali disponibili
- Raggruppamento per nazione
"""

import requests
import json
import re
from datetime import datetime


# ============================================================================
# CONFIGURAZIONE
# ============================================================================

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
    'Finlandia': '🇫🇮', 'Internazionale': '🌍',
}

# Emoji bandiere per codice lingua ISO
LANGUAGE_FLAG_EMOJI = {
    'it': '🇮🇹', 'gb': 'eng', 'es': '🇪🇸', 'de': '🇩🇪', 'fr': '🇫🇷',
    'us': '🇺🇸', 'ca': '🇨🇦', 'pt': '🇵🇹', 'nl': '🇳🇱', 'be': '🇧🇪',
    'tr': '🇹🇷', 'se': '🇸🇪', 'gr': '🇬🇷', 'cz': '🇨🇿', 'fi': '🇫🇮',
}


def get_country_code_from_league(league):
    """Estrae codice paese dal campionato"""
    league_lower = league.lower()
    for key, code in LEAGUE_TO_COUNTRY.items():
        if key in league_lower:
            return code
    return None


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


def generate_grouped_json(events):
    """Genera JSON raggruppato per nazione usando link sansat"""
    
    countries_dict = {}
    total_channels = 0
    events_processed = 0
    
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
        
        event_title = f'{team1} vs {team2}' if team1 and team2 else (team1 or 'Live Event')
        event_channels = match.get('channels', [])
        
        channels_found = []
        
        for ch in event_channels:
            # Estrai info canale
            channel_name = ch.get('name', '')
            channel_language = ch.get('language', '').lower()
            sansat_id = extract_sansat_id(ch)
            
            if sansat_id:
                # Emoji bandiera per lingua
                flag = LANGUAGE_FLAG_EMOJI.get(channel_language, '📡')
                
                # Titolo con bandiera
                title = f"[COLOR cyan][{time_str}][/COLOR] "
                title += f"[COLOR gold]{event_title}[/COLOR] - "
                title += f"{flag} {channel_name}"
                
                info = f"{full_datetime} - {league}"
                
                channel_item = {
                    "title": title,
                    "myresolve": f"sansat@@{sansat_id}",
                    "thumbnail": "https://cdn-icons-png.flaticon.com/512/3524/3524659.png",
                    "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg",
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
        flag = COUNTRY_FLAGS.get(country, '🌍')
        separator = {
            "title": f"[B][COLOR yellow]═══ {flag} {country.upper()} ═══[/COLOR][/B]",
            "link": "ignoreme",
            "thumbnail": "https://cdn-icons-png.flaticon.com/512/814/814346.png",
            "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg",
            "info": f"Eventi {country}"
        }
        final_json['items'].append(separator)
        
        # Items della nazione
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
    print("║" + " "*15 + "GENERATORE EVENTI LIVE - VERSIONE SANSAT" + " "*24 + "║")
    print("╚" + "="*78 + "╝\n")
    
    # 1. Eventi
    print("STEP 1: Download eventi sportivi")
    print("-" * 80)
    events = fetch_sports_events()
    
    if not events:
        print("\n❌ Nessun evento trovato!")
        exit(1)
    
    # 2. Genera JSON con link sansat
    print("\nSTEP 2: Generazione eventi con link sansat@@ID")
    print("-" * 80)
    json_data = generate_grouped_json(events)
    
    if not json_data['items']:
        print("\n⚠ Nessun canale disponibile!")
        exit(1)
    
    # 3. Salva
    print("\nSTEP 3: Salvataggio")
    print("-" * 80)
    save_json(json_data)
    
    print("\n" + "="*80)
    print("✅ COMPLETATO!")
    print("="*80)
    print("\n💡 FEATURES:")
    print("  ✓ Usa direttamente link sansat@@ da super.league.do")
    print("  ✓ NO matching necessario!")
    print("  ✓ TUTTI i canali disponibili automaticamente")
    print("  ✓ Raggruppamento per nazione (Italia prima)")
    print("  ✓ Ordinamento cronologico")
    print("  ✓ Bandiere per ogni canale (IT/GB/ES/DE...)")
