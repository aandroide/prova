# -*- coding: utf-8 -*-
"""
GENERATORE EVENTI LIVE RAGGRUPPATO PER NAZIONE

Author: Androide

"""

import requests
import json
import re
from datetime import datetime


# ============================================================================
# CONFIGURAZIONE
# ============================================================================

MANDRAKODI_CANALI_URL = 'https://raw.githubusercontent.com/aandroide/prova/refs/heads/main/canali/canali.json'
SUPERLEAGUE_URL = 'https://super.league.do'


# Mapping campionati → nazioni
LEAGUE_TO_COUNTRY = {
    # Italia
    'italy': 'Italia',
    'serie a': 'Italia',
    'serie b': 'Italia',
    'coppa italia': 'Italia',
    
    # Inghilterra
    'england': 'Inghilterra',
    'premier league': 'Inghilterra',
    'championship': 'Inghilterra',
    'fa cup': 'Inghilterra',
    'efl cup': 'Inghilterra',
    
    # Spagna
    'spain': 'Spagna',
    'laliga': 'Spagna',
    'la liga': 'Spagna',
    'copa del rey': 'Spagna',
    
    # Germania
    'germany': 'Germania',
    'bundesliga': 'Germania',
    
    # Francia
    'france': 'Francia',
    'ligue 1': 'Francia',
    
    # Europa (coppe)
    'champions league': 'Europa',
    'europa league': 'Europa',
    'conference league': 'Europa',
    'uefa': 'Europa',
    
    # USA
    'nba': 'USA',
    'nfl': 'USA',
    'mlb': 'USA',
    'nhl': 'USA',
    'mls': 'USA',
    
    # Altri
    'portugal': 'Portogallo',
    'netherlands': 'Olanda',
    'belgium': 'Belgio',
    'turkey': 'Turchia',
}


COUNTRY_FLAGS = {
    'Italia',
    'Inghilterra',
    'Spagna',
    'Germania',
    'Francia',
    'Europa',
    'USA',
    'Portogallo',
    'Olanda',
    'Belgio',
    'Turchia',
}


def get_country_from_league(league):
    """Identifica la nazione dal nome del campionato"""
    league_lower = league.lower()
    
    for key, country in LEAGUE_TO_COUNTRY.items():
        if key in league_lower:
            return country
    
    # Default: Altri
    return 'Altri'


def download_mandrakodi_channels(url=MANDRAKODI_CANALI_URL):
    """Scarica canali MandraKodi da GitHub"""
    try:
        print(f"📡 Downloading canali MandraKodi da GitHub...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 403:
            print("\n❌ ERRORE 403 FORBIDDEN!")
            print("   Repository privato. Rendi pubblico su GitHub.")
            return []
        
        if response.status_code != 200:
            print(f"❌ Errore HTTP: {response.status_code}")
            return []
        
        data = json.loads(response.text)
        
        channels = []
        for item in data.get('items', []):
            title = item.get('title', '')
            clean_name = re.sub(r'\[COLOR [^\]]+\]|\[/COLOR\]|\(ITA\)|\(ENG\)|\(ESP\)|\(FRA\)', '', title).strip()
            
            channels.append({
                'name': clean_name,
                'original_title': title,
                'thumbnail': item.get('thumbnail', ''),
                'stream': item.get('myresolve', ''),
                'fanart': item.get('fanart', 'https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg'),
                'info': item.get('info', ''),
                'enabled': item.get('enabled', 0)
            })
        
        print(f"✓ Scaricati {len(channels)} canali")
        return channels
    
    except Exception as e:
        print(f"❌ Errore: {e}")
        return []


def fetch_sports_events(url=SUPERLEAGUE_URL):
    """Scarica eventi da super.league.do"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36'
    }
    
    try:
        print(f"📡 Downloading eventi sportivi...")
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
        
        # Pattern VECCHIO
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


def find_mandrakodi_channel(channel_name, mandrakodi_channels):
    """Cerca canale in lista MandraKodi"""
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
    """
    Genera JSON raggruppato per NAZIONE
    Italia SEMPRE prima, poi altre nazioni ordinate
    Dentro ogni nazione: ordinato per orario crescente
    """
    
    # Dizionario: nazione → lista items
    countries_dict = {}
    
    total_channels_added = 0
    events_processed = 0
    
    for match in events:
        team1 = match.get('team1', '')
        team2 = match.get('team2', '')
        league = match.get('league', '')
        sport = match.get('sport', '')
        
        # Identifica nazione
        country = get_country_from_league(league)
        
        # Timestamp
        try:
            timestamp = match.get('startTimestamp', 0)
            if timestamp:
                start_time = datetime.fromtimestamp(timestamp / 1000)
                date_str = start_time.strftime('%d-%b')
                time_str = start_time.strftime('%H:%M')
                full_datetime = start_time.strftime('%d-%b %H:%M')
                sort_timestamp = timestamp
            else:
                date_str = '?'
                time_str = '?'
                full_datetime = 'Orario da definire'
                sort_timestamp = 9999999999999
        except:
            date_str = '?'
            time_str = '?'
            full_datetime = 'Orario da definire'
            sort_timestamp = 9999999999999
        
        event_title = f'{team1} vs {team2}' if team1 and team2 else (team1 or 'Live Event')
        event_channels = match.get('channels', [])
        
        channels_found = []
        
        for ch in event_channels:
            if isinstance(ch, str):
                channel_name = ch
            elif isinstance(ch, dict):
                channel_name = ch.get('name', '')
            else:
                continue
            
            if not channel_name:
                continue
            
            mk_ch = find_mandrakodi_channel(channel_name, mandrakodi_channels)
            
            if mk_ch and mk_ch['stream']:
                channels_found.append(mk_ch)
        
        # Se l'evento ha almeno un canale
        if channels_found:
            events_processed += 1
            
            # Inizializza lista nazione se non esiste
            if country not in countries_dict:
                countries_dict[country] = []
            
            # Aggiungi OGNI canale
            for mk_ch in channels_found:
                # Titolo: [ORARIO] EVENTO - CANALE
                title = f"[COLOR cyan][{time_str}][/COLOR] "
                title += f"[COLOR gold]{event_title}[/COLOR] - "
                title += f"{mk_ch['original_title']}"
                
                # Info: DATA ORA - CAMPIONATO
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
                total_channels_added += 1
    
    # ORDINA items dentro ogni nazione per timestamp
    for country in countries_dict:
        countries_dict[country].sort(key=lambda x: x['_timestamp'])
    
    # ORDINA nazioni: Italia prima, poi altre alfabeticamente
    sorted_countries = []
    
    if 'Italia' in countries_dict:
        sorted_countries.append('Italia')
    
    other_countries = sorted([c for c in countries_dict.keys() if c != 'Italia'])
    sorted_countries.extend(other_countries)
    
    # Crea JSON finale con separatori
    final_json = {
        "SetViewMode": "55",
        "items": []
    }
    
    for country in sorted_countries:
        # Aggiungi SEPARATORE nazione
        flag = COUNTRY_FLAGS.get(country, '🌍')
        separator = {
            "title": f"[B][COLOR yellow]═══ {flag} {country.upper()} ═══[/COLOR][/B]",
            "link": "ignoreme",
            "thumbnail": "https://cdn-icons-png.flaticon.com/512/814/814346.png",
            "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg",
            "info": f"Eventi {country}"
        }
        final_json['items'].append(separator)
        
        # Aggiungi items della nazione
        for item in countries_dict[country]:
            del item['_timestamp']  # Rimuovi timestamp temporaneo
            final_json['items'].append(item)
    
    print(f"\n📊 Statistiche:")
    print(f"  ✓ Eventi processati: {events_processed}")
    print(f"  ✓ Canali totali: {total_channels_added}")
    print(f"  ✓ Nazioni trovate: {len(countries_dict)}")
    print(f"  ✓ Lista raggruppata per nazione (Italia prima)")
    
    return final_json


def save_single_json(json_data, filename='EVENTI_LIVE.json'):
    """Salva UN SOLO file JSON"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ File salvato: {filename}")
    
    return filename


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("╔" + "="*78 + "╗")
    print("║" + " "*8 + "GENERATORE EVENTI LIVE - RAGGRUPPATO PER NAZIONE" + " "*21 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    # 1. Scarica canali
    print("STEP 1: Download canali MandraKodi")
    print("-" * 80)
    mandrakodi_channels = download_mandrakodi_channels()
    
    if not mandrakodi_channels:
        print("\n❌ IMPOSSIBILE CONTINUARE!")
        exit(1)
    
    # 2. Scarica eventi
    print("\nSTEP 2: Download eventi sportivi")
    print("-" * 80)
    events = fetch_sports_events()
    
    if not events:
        print("\n❌ Nessun evento trovato!")
        exit(1)
    
    # 3. Genera JSON raggruppato
    print("\nSTEP 3: Raggruppamento per nazione + ordinamento")
    print("-" * 80)
    grouped_json = generate_grouped_json(events, mandrakodi_channels)
    
    if not grouped_json['items']:
        print("\n⚠ Nessun canale disponibile!")
        exit(1)
    
    # 4. Salva
    print("\nSTEP 4: Salvataggio file")
    print("-" * 80)
    save_single_json(grouped_json)
    
    print("\n✅ COMPLETATO!")
    print("\n💡 Generato file: EVENTI_LIVE.json")
    print("   Raggruppato per nazione (Italia prima)")
    print("   Ordinato per orario dentro ogni nazione")
