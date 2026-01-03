# -*- coding: utf-8 -*-
"""
GENERATORE EVENTI LIVE MANDRAKODI - TUTTI I CANALI INSIEME
===========================================================
- Ogni evento va nella nazione del suo campionato
- Mostra TUTTI i canali disponibili (italiani + stranieri)
- Un JSON per ogni nazione
- DIZIONARIO CANALI HARDCODATO (nessun download esterno)
"""

import requests
import json
import re
from datetime import datetime, timedelta
import os

# ============================================================================
# CONFIGURAZIONE
# ============================================================================

GITHUB_USERNAME = 'aandroide'  # <-- MODIFICA QUESTO!
SUPERLEAGUE_URL = 'https://super.league.do'
GITHUB_RAW_BASE = f'https://raw.githubusercontent.com/{GITHUB_USERNAME}/prova/main/outputs'

# DIZIONARIO CANALI - GENERATO AUTOMATICAMENTE
MANDRAKODI_CHANNELS = {
    "3cat": {
        "name": "3 CAT",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Logotip_de_3Cat.svg/512px-Logotip_de_3Cat.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "6ter": {
        "name": "6TER",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Logo_6ter_2016.svg/512px-Logo_6ter_2016.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "aclcornhole": {
        "name": "ACL CORNHOLE",
        "thumbnail": "https://shop.iplayacl.com/cdn/shop/files/ACL-logo_1024x1024_2x_7dadb088-234f-4d59-a1ef-a81586b9a75d.jpg?v=1750443581&width=512",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport1": {
        "name": "Arena Sport 1",
        "thumbnail": "https://iptvboss.xyz/logos/Bosnia/ArenaSport1.bh.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport10": {
        "name": "Arena Sport 10",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/8/89/As101.png/revision/latest/scale-to-width-down/300?cb=20221111132559",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport1premium": {
        "name": "Arena Sport 1 Premium",
        "thumbnail": "https://www.supernovabih.ba/wp-content/uploads/2022/06/arena-premium-1-hd.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport2": {
        "name": "Arena Sport 2",
        "thumbnail": "https://iptvboss.xyz/logos/Bosnia/ArenaSport2.bh.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport2premium": {
        "name": "Arena Sport 2 Premium",
        "thumbnail": "https://www.supernovabih.ba/wp-content/uploads/2022/06/arena-premium-2-hd.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport3": {
        "name": "Arena Sport 3",
        "thumbnail": "https://iptvboss.xyz/logos/Bosnia/ArenaSport3.bh.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport4": {
        "name": "Arena Sport 4",
        "thumbnail": "https://iptvboss.xyz/logos/Bosnia/ArenaSport4.bh.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport5": {
        "name": "Arena Sport 5",
        "thumbnail": "https://iptvboss.xyz/logos/Bosnia/ArenaSport5.bh.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport6": {
        "name": "Arena Sport 6",
        "thumbnail": "https://iptvboss.xyz/logos/Bosnia/ArenaSport6.bh.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport7": {
        "name": "Arena Sport 7",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/a/a2/ARENASPORT_7.png/revision/latest/scale-to-width-down/300?cb=20221111131652",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport8": {
        "name": "Arena Sport 8",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/4/4e/ARENASPORT_8.png/revision/latest/scale-to-width-down/300?cb=20221111132134",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "arenasport9": {
        "name": "Arena Sport 9",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/b/b8/As91.png/revision/latest/scale-to-width-down/300?cb=20221111132431",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "beinsport1": {
        "name": "BEIN SPORT 1",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Logo_bein_sports_1.png/512px-Logo_bein_sports_1.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "beinsport2": {
        "name": "BEIN SPORT 2",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Logo_bein_sports_2.png/512px-Logo_bein_sports_2.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "beinsport3": {
        "name": "BEIN SPORT 3",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Logo_bein_sports_3.png/512px-Logo_bein_sports_3.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "billiardtv": {
        "name": "BILLIARD TV",
        "thumbnail": "https://image.discovery.indazn.com/ca/v2/ca/image?id=vrel7rmw9vte1rnw6un6vq9dl_image-header_pUs_1715792122000&quality=70",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "bluezoom": {
        "name": "BLUE ZOOM",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/fr/f/f0/Blue_Zoom.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "bundesliga1": {
        "name": "Bundesliga 1",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/9/98/Logo_Bundesliga.svg/512px-Logo_Bundesliga.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "bundesliga2": {
        "name": "Bundesliga 2",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/9/98/Logo_Bundesliga.svg/512px-Logo_Bundesliga.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "bundesliga3": {
        "name": "Bundesliga 3",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/9/98/Logo_Bundesliga.svg/512px-Logo_Bundesliga.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "bundesliga4": {
        "name": "Bundesliga 4",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/9/98/Logo_Bundesliga.svg/512px-Logo_Bundesliga.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "bundesliga5": {
        "name": "Bundesliga 5",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/9/98/Logo_Bundesliga.svg/512px-Logo_Bundesliga.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "bundesliga6": {
        "name": "Bundesliga 6",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/9/98/Logo_Bundesliga.svg/512px-Logo_Bundesliga.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "bundesliga7": {
        "name": "Bundesliga 7",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/9/98/Logo_Bundesliga.svg/512px-Logo_Bundesliga.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "bundesliga8": {
        "name": "Bundesliga 8",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/9/98/Logo_Bundesliga.svg/512px-Logo_Bundesliga.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "cbssport": {
        "name": "CBS SPORT",
        "thumbnail": "https://d3g9pb5nvr3u7.cloudfront.net/sites/55520d5de45dba1b5e10ac70/1189012733/256.jpg",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "cosmotesport1": {
        "name": "COSMOTE SPORT 1",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-cosmote-sport-1-383.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "cosmotesport2": {
        "name": "COSMOTE SPORT 2",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-cosmote-sport-2-384.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "cosmotesport3": {
        "name": "COSMOTE SPORT 3",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-cosmote-sport-3-385.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "cosmotesport4": {
        "name": "COSMOTE SPORT 4",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-cosmote-sport-4-386.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "cosmotesport5": {
        "name": "COSMOTE SPORT 5",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-cosmote-sport-5-387.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "cosmotesport6": {
        "name": "COSMOTE SPORT 6",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-cosmote-sport-6-388.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "cosmotesport7": {
        "name": "COSMOTE SPORT 7",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-cosmote-sport-7-389.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "cosmotesport8": {
        "name": "COSMOTE SPORT 8",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-cosmote-sport-8-390.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "cosmotesport9": {
        "name": "COSMOTE SPORT 9",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-cosmote-sport-9-1590.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "daserste": {
        "name": "DAS ERSTE",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Das_Erste-Logo.svg/640px-Das_Erste-Logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "dazn1": {
        "name": "DAZN 1",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-dazn-1-es-2510.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "dazn1eventonly": {
        "name": "DAZN 1 (Event Only)",
        "thumbnail": "https://i.imgur.com/8FRcfhP.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "dazn2": {
        "name": "DAZN 2",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-dazn-2-es-2511.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "dazn2eventonly": {
        "name": "DAZN 2 (Event Only)",
        "thumbnail": "https://i.imgur.com/8FRcfhP.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "dazn3": {
        "name": "DAZN 3",
        "thumbnail": "https://3038.images-vfp2.ott.kaltura.com/Service.svc/GetImage/p/3038/entry_id/270837cf317d40308022c27e2900f8d8/version/1",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "dazn4": {
        "name": "DAZN 4",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/d/df/DAZN_4_FHD.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "dazn5": {
        "name": "DAZN 5",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/b/b9/DAZN_5_2024.svg/revision/latest/scale-to-width-down/512?cb=20240713211021",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "dazn6": {
        "name": "DAZN 6",
        "thumbnail": "https://3038.images-vfp2.ott.kaltura.com/Service.svc/GetImage/p/3038/entry_id/67e734ee68de4f2ba002c89d4bc0dc30/version/1",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "daznboxe": {
        "name": "DAZN BOXE",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-dazn-nl-2677.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "daznf1": {
        "name": "DAZN F1",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-dazn-formula-1-366.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "daznfast": {
        "name": "DAZN FAST+",
        "thumbnail": "https://images.samsung.com/is/image/samsung/assets/de/explore/entertainment/your-sportsummer-on-samsung-tv-plus/DAZN-FastPlus_Logos_1x1_Square_1000x1000.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "daznpga": {
        "name": "DAZN PGA",
        "thumbnail": "https://insidegolf.ca/images/18.01.27-PGATour-DAZN.jpg",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "daznppv1": {
        "name": "DAZN PPV 1",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/2/29/DAZN_PPV.png/revision/latest?cb=20230708104557",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "daznppv2": {
        "name": "DAZN PPV 2",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/2/29/DAZN_PPV.png/revision/latest?cb=20230708104557",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "daznppv3": {
        "name": "DAZN PPV 3",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/2/29/DAZN_PPV.png/revision/latest?cb=20230708104557",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "daznppv4": {
        "name": "DAZN PPV 4",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/2/29/DAZN_PPV.png/revision/latest?cb=20230708104557",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "daznppv5": {
        "name": "DAZN PPV 5",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/2/29/DAZN_PPV.png/revision/latest?cb=20230708104557",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "daznrise": {
        "name": "DAZN RISE",
        "thumbnail": "https://www.blm.de/files/png3/logo_dazn_rise.jpg",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "dmax": {
        "name": "DMAX",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/DMAX_-_Logo_2016.svg/512px-DMAX_-_Logo_2016.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "dubaisport1": {
        "name": "DUBAI SPORT 1",
        "thumbnail": "https://smotret.tv/images/dubai-sports.webp",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "dubaisport2": {
        "name": "DUBAI SPORT 2",
        "thumbnail": "https://dn710009.ca.archive.org/0/items/dubai-sports-2/Dubai%20Sports%202.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "elevensport1": {
        "name": "Eleven Sport 1",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/kih3iw1701160131.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "elevensport14k": {
        "name": "Eleven Sport 1 4K",
        "thumbnail": "https://net4me.info/wp-content/uploads/2020/07/elevensports1_4k_1-632x221-1.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "elevensport2": {
        "name": "Eleven Sport 2",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/y37tax1701160140.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "elevensport3": {
        "name": "Eleven Sport 3",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/7gnrhg1701160157.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "elevensport4": {
        "name": "Eleven Sport 4",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/kjp6lk1701160165.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "espn": {
        "name": "ESPN",
        "thumbnail": "https://www.thesportsdb.com/images/media/channel/logo/wc8dnt1660760493.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "espn1": {
        "name": "ESPN 1",
        "thumbnail": "https://www.thesportsdb.com/images/media/channel/logo/wc8dnt1660760493.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "espn2": {
        "name": "ESPN 2",
        "thumbnail": "https://www.thesportsdb.com/images/media/channel/logo/keezdj1660760512.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "espn3": {
        "name": "ESPN 3",
        "thumbnail": "https://www.thesportsdb.com/images/media/channel/logo/x8t6yd1660760523.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "espn4": {
        "name": "ESPN 4",
        "thumbnail": "https://www.thesportsdb.com/images/media/channel/logo/ekdzvo1660760535.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "eurosport": {
        "name": "EuroSport",
        "thumbnail": "https://cdn.broadbandtvnews.com/wp-content/uploads/2015/11/14120517/Eurosport-logo-symbol.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "eurosport1": {
        "name": "EuroSport 1",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Eurosport_1_Logo_2015.svg/512px-Eurosport_1_Logo_2015.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "eurosport2": {
        "name": "EuroSport 2",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Eurosport_2_Logo_2015.svg/512px-Eurosport_2_Logo_2015.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "eurosport3": {
        "name": "EuroSport 3",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/4/41/Eurosport_3_%28II%29.svg/revision/latest/scale-to-width-down/512",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "eurosport4": {
        "name": "EuroSport 4",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/3/3d/Eurosport_4_%28II%29.svg/revision/latest/scale-to-width-down/512",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "eurosport5": {
        "name": "EuroSport 5",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/2/2b/Eurosport_5_%28II%29.svg/revision/latest/scale-to-width-down/512",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "eurosport6": {
        "name": "EuroSport 6",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/9/91/Eurosport_6_%28II%29.svg/revision/latest/scale-to-width-down/512",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "foxsports1": {
        "name": "Fox Sports 1",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Fox_Sports_1_logo.svg/512px-Fox_Sports_1_logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "foxsports2": {
        "name": "Fox Sports 2",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Fox_sports_2_logo.svg/512px-Fox_sports_2_logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "france2": {
        "name": "FRANCE 2",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/3/33/France_2_logo.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "france3": {
        "name": "FRANCE 3",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/8/8a/France_3_logo.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "france4": {
        "name": "FRANCE 4",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/7/73/France_4_logo.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "france5": {
        "name": "FRANCE 5",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/0/01/France_5_logo.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "fubotv1": {
        "name": "FUBOTV 1",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Fubo_2023.svg/250px-Fubo_2023.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "fubotv2": {
        "name": "FUBOTV 2",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Fubo_2023.svg/250px-Fubo_2023.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "go3sport1": {
        "name": "GO3 Sport 1",
        "thumbnail": "https://www.thesportsdb.com/images/media/channel/logo/qo7ct61723836245.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "go3sport2": {
        "name": "GO3 Sport 2",
        "thumbnail": "https://www.thesportsdb.com/images/media/channel/logo/14ktq21723836456.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "go3sport3": {
        "name": "GO3 Sport 3",
        "thumbnail": "https://www.thesportsdb.com/images/media/channel/logo/clcnt51723874834.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "go3sport4": {
        "name": "GO3 Sport 4",
        "thumbnail": "https://i.imgur.com/WBLF0CX.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "go3sportopen": {
        "name": "GO3 Sport Open",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Go3_Sport_Open_Logo_2023.svg/512px-Go3_Sport_Open_Logo_2023.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "infosport": {
        "name": "INFOSPORT+",
        "thumbnail": "https://img.favpng.com/5/20/0/infosport-television-channel-logo-sky-news-png-favpng-EMzQL770aZF3qpYbYswTzvLmx.jpg",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "intertv": {
        "name": "INTER TV",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Inter_TV_-_Logo_2021.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "la1": {
        "name": "LA 1",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/7/76/La_1_HD_TVE.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "lequipe": {
        "name": "L'EQUIPE",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/L_Equipe_Logo.svg/512px-L_Equipe_Logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "ligatv": {
        "name": "LIGA TV",
        "thumbnail": "https://pbs.twimg.com/profile_images/1747989339764572160/7nxm03-2_400x400.jpg",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "m6": {
        "name": "M6",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/a/a2/M6_logo_new-1-.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "milantv": {
        "name": "MILAN TV",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/e/eb/Milan_TV_-_Logo_2016.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "nbatv": {
        "name": "NBA TV",
        "thumbnail": "https://3038.images-vfp2.ott.kaltura.com/Service.svc/GetImage/p/3038/entry_id/36d1bbd4b0144a19bdb6ec2a834a45b9/version/0",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "nbc": {
        "name": "NBC",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/NBC_logo.svg/512px-NBC_logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "nbcktvb": {
        "name": "NBC KTVB",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/KTVB_NBC_7_Boise%2C_Idaho_Logo.svg/512px-KTVB_NBC_7_Boise%2C_Idaho_Logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "nbcuniverso": {
        "name": "NBC UNIVERSO",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/8/88/Universo_2017.svg/revision/latest/scale-to-width-down/512?cb=20170329072546",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "nflnetwork": {
        "name": "NFL NETWORK",
        "thumbnail": "https://www.touchdown.it/wp-content/uploads/2018/09/dazn-nfl-in-tv-2018.jpg",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "npo1": {
        "name": "NPO 1",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/7/7d/NPO_1_logo_2014.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "npo2": {
        "name": "NPO 2",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/NPO_3_logo_2014.svg/512px-NPO_3_logo_2014.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "npo3": {
        "name": "NPO 3",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/NPO_3_logo_2014.svg/512px-NPO_3_logo_2014.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "other": {
        "name": "OTHER",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Fubo_2023.svg/250px-Fubo_2023.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "playsports1": {
        "name": "Play Sports 1",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/e/ec/Play_Sports_1_2021.svg/revision/latest/scale-to-width-down/512?cb=20230830090028",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "playsports2": {
        "name": "Play Sports 2",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/3/3f/Play_Sports_2_2021.svg/revision/latest/scale-to-width-down/512?cb=20230830090151",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "playsports3": {
        "name": "Play Sports 3",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/4/4a/Play_Sports_3_2021.svg/revision/latest/scale-to-width-down/512?cb=20230830090305",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "pll": {
        "name": "PLL",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/en/thumb/8/8f/Premier_Lacrosse_League_logo.svg/512px-Premier_Lacrosse_League_logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "powersports": {
        "name": "POWER SPORTS",
        "thumbnail": "https://images.fubo.tv/channel-config-ui/station-logos/on-white/psw---color-logo-evann-dadamo.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "premieresport1": {
        "name": "Premiere Sport 1",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/Premier_Sports.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "premieresport2": {
        "name": "Premiere Sport 2",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/Premier_Sports.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "premieresport3": {
        "name": "PREMIERE SPORT 3",
        "thumbnail": "https://static.wikia.nocookie.net/logo-timeline/images/0/04/Premiere_2017.png/revision/latest/scale-to-width-down/512",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "premieresport4": {
        "name": "PREMIERE SPORT 4",
        "thumbnail": "https://static.wikia.nocookie.net/logo-timeline/images/0/04/Premiere_2017.png/revision/latest/scale-to-width-down/512",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "premieresport5": {
        "name": "PREMIERE SPORT 5",
        "thumbnail": "https://static.wikia.nocookie.net/logo-timeline/images/0/04/Premiere_2017.png/revision/latest/scale-to-width-down/512",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "premieresport6": {
        "name": "PREMIERE SPORT 6",
        "thumbnail": "https://static.wikia.nocookie.net/logo-timeline/images/0/04/Premiere_2017.png/revision/latest/scale-to-width-down/512",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "premieresport7": {
        "name": "PREMIERE SPORT 7",
        "thumbnail": "https://static.wikia.nocookie.net/logo-timeline/images/0/04/Premiere_2017.png/revision/latest/scale-to-width-down/512",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "premieresport8": {
        "name": "PREMIERE SPORT 8",
        "thumbnail": "https://static.wikia.nocookie.net/logo-timeline/images/0/04/Premiere_2017.png/revision/latest/scale-to-width-down/512",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "radiotvseriea": {
        "name": "RADIO TV SERIE A",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/a/af/Radio_TV_Serie_A_con_RDS.svg/512px-Radio_TV_Serie_A_con_RDS.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "raisport": {
        "name": "RAI SPORT",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/b/bc/RAI_Sport_Logo.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "rallytv": {
        "name": "Rally TV",
        "thumbnail": "https://www.punto-informatico.it/app/uploads/2024/05/rally_tv_dazn.jpg",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "rsila1": {
        "name": "RSI LA1",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/5/51/RSI_La_1.svg/512px-RSI_La_1.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "rsila2": {
        "name": "RSI LA2",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/RSI_La_2_2012.svg/512px-RSI_La_2_2012.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "rteone": {
        "name": "RTE ONE",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e4/RT _One_2014.svg/512px-RT _One_2014.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "rtetwo": {
        "name": "RTE TWO",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/fr/0/01/RTE_Two.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "rtl1": {
        "name": "RTL 1",
        "thumbnail": "https://static.wikia.nocookie.net/logosfake/images/c/c5/RTL_1_1991.png/revision/latest/scale-to-width-down/512?cb=20150929185306",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "rtl2": {
        "name": "RTL 2",
        "thumbnail": "https://static.wikia.nocookie.net/logosfake/images/3/3d/RTL_2_1991.png/revision/latest/scale-to-width-down/512?cb=20151001133206",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "rtl3": {
        "name": "RTL 3",
        "thumbnail": "https://static.wikia.nocookie.net/logosfake/images/5/5c/RTL_3_1991.png/revision/latest/scale-to-width-down/512?cb=20151002131745",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "setantasport1": {
        "name": "Setanta Sport 1",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/f/f4/Setanta_Sports_1_2011.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "setantasport2": {
        "name": "Setanta Sport 2",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/ujxkqz1589620867.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysport1": {
        "name": "SKY SPORT 1",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/2/27/Sky_Sport_1_NZ.svg/revision/latest/scale-to-width-down/512?cb=20230830144011",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysport2": {
        "name": "SKY SPORT 2",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/8/88/Sky_Sport_2_NZ.svg/revision/latest/scale-to-width-down/512?cb=20230830144002",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysport3": {
        "name": "SKY SPORT 3",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/5/5d/Sky_Sport_3_NZ.svg/revision/latest/scale-to-width-down/512?cb=20230830143951",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysport4": {
        "name": "SKY SPORT 4",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/9/90/Sky_Sport_4_NZ.svg/revision/latest/scale-to-width-down/512?cb=20230830143941",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysport5": {
        "name": "SKY SPORT 5",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/2/23/Sky_Sport_5_NZ.svg/revision/latest/scale-to-width-down/512?cb=20230830143710",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysport6": {
        "name": "SKY SPORT 6",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/8/80/Sky_Sport_6_NZ.svg/revision/latest/scale-to-width-down/512?cb=20230830143701",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysport7": {
        "name": "SKY SPORT 7",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/f/f4/Sky_Sport_7_NZ.svg/revision/latest/scale-to-width-down/512?cb=20230830143651",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysport8": {
        "name": "SKY SPORT 8",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/e/ee/Sky_Sport_8_NZ.svg/revision/latest/scale-to-width-down/512?cb=20230830143641",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysport9": {
        "name": "SKY SPORT 9",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/0/00/Sky_Sport_9_NZ.svg/revision/latest/scale-to-width-down/512?cb=20230830143632",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysports1": {
        "name": "Sky Sports 1",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-sky-sport-hd-1-155.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysports2": {
        "name": "Sky Sports 2",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-sky-sport-hd-2-171.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysports3": {
        "name": "Sky Sports 3",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-sky-sport-3-1621.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysports4": {
        "name": "Sky Sports 4",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-sky-sport-4-de-1622.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysports5": {
        "name": "Sky Sports 5",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-sky-sport-5-1623.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysports6": {
        "name": "Sky Sports 6",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-sky-sport-6-1624.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysportsf1": {
        "name": "Sky Sports F1",
        "thumbnail": "https://img2.sport-tv-guide.live/images/tv-station-sky-sport-hd-1-155.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysportslaliga": {
        "name": "Sky Sports La Liga",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/3/30/Sky_Sports_LaLiga.svg/revision/latest/scale-to-width-down/512?cb=2023112014424",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "skysporttopevent": {
        "name": "Sky Sport TOP EVENT",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/r14o5i1658662835.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "sport1": {
        "name": "SPORT 1",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/t1k26d1616932441.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "sport2": {
        "name": "SPORT 2",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/68s5x31616932507.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "sportnet": {
        "name": "SPORT NET",
        "thumbnail": "https://images-cdn4.welcomesoftware.com/assets/SportsNet.webp/Zz0wYWQ0YTc0MDFjNTAxMWVlOWE4MzNlMWYyZGIwZTJhMw==",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "sporttv1": {
        "name": "Sport TV 1",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/vy9kl11700902598.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "sporttv2": {
        "name": "Sport TV 2",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/oiu2yn1700902611.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "sporttv3": {
        "name": "Sport TV 3",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/fjy5d31700902671.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "sporttv4": {
        "name": "Sport TV 4",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/wzqgsk1700902680.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "sporttv5": {
        "name": "Sport TV 5",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/ldsp6c1700902696.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "sporttv6": {
        "name": "Sport TV 6",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/1ajyjo1700902708.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "sporttv7": {
        "name": "Sport TV 7",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/f/f3/Sport_TV7_%282024%29.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "spotv": {
        "name": "SPOTV",
        "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJS9GV5Qj5cy-9FxVuTcWTam2D3Ftm_wOPiw&s",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "spotv2": {
        "name": "SPOTV 2",
        "thumbnail": "https://static.wikia.nocookie.net/logopedia/images/6/68/SPOTV2_logo_2018.png/revision/latest?cb=20230507021015",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "starzplay1": {
        "name": "STARZPLAY 1",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Starzplay-logo.svg/640px-Starzplay-logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "starzplay2": {
        "name": "STARZPLAY 2",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Starzplay-logo.svg/640px-Starzplay-logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tf1": {
        "name": "TF1",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/TF1_logo_2006.svg/512px-TF1_logo_2006.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tntsport1": {
        "name": "TNT Sport 1",
        "thumbnail": "https://tv.assets.pressassociation.io/d45290f3-96f2-53d3-b83f-bd875c745f83.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tntsport2": {
        "name": "TNT Sport 2",
        "thumbnail": "https://tv.assets.pressassociation.io/1fda8663-f68a-5cc4-afd0-0e846e2ba265.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tntsport3": {
        "name": "TNT Sport 3",
        "thumbnail": "https://tv.assets.pressassociation.io/04f0dc31-ed4e-5a13-98cc-32e612a3fcc6.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tntsport4": {
        "name": "TNT Sport 4",
        "thumbnail": "https://tv.assets.pressassociation.io/e98a3304-0e26-5eed-bc55-071e69a15bf8.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tntsport5": {
        "name": "TNT Sport 5",
        "thumbnail": "https://tv.assets.pressassociation.io/f25e3499-4757-57ac-90e7-cba823730841.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tsn1": {
        "name": "TSN 1",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/8/82/TSN_logo.svg/512px-TSN_logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tsn2": {
        "name": "TSN 2",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/8/82/TSN_logo.svg/512px-TSN_logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tsn3": {
        "name": "TSN 3",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/8/82/TSN_logo.svg/512px-TSN_logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tsn4": {
        "name": "TSN 4",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/8/82/TSN_logo.svg/512px-TSN_logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tsn5": {
        "name": "TSN 5",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/it/thumb/8/82/TSN_logo.svg/512px-TSN_logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tv4sportlive1": {
        "name": "TV4 Sport Live 1",
        "thumbnail": "https://www.telia.se/images/j6b4qnxw7ufu/25XzA8bRGUMxcIwr5EzXtJ/92e5b953dc767e929dfc63e3a03699ca/tv4_sport_live_1.png?fit=scale&w=256&fm=webp&q=75&h=256",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tv4sportlive2": {
        "name": "TV4 Sport Live 2",
        "thumbnail": "https://www.telia.se/images/j6b4qnxw7ufu/6qU6aJGG9kgAECw6c3xpEm/79fde1c03151b9bcee3a276eb4e23d55/tv4_sport_live_2.png?fit=scale&w=256&fm=webp&q=75&h=256",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tv4sportlive3": {
        "name": "TV4 Sport Live 3",
        "thumbnail": "https://www.telia.se/images/j6b4qnxw7ufu/3y0AxGHgQlHMF8nZSoDB8M/2b2e3e69b49597b0c04d072b400e3e4d/tv4_sport_live_3.png?fit=scale&w=256&fm=webp&q=75&h=256",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "tv4sportlive4": {
        "name": "TV4 Sport Live 4",
        "thumbnail": "https://www.telia.se/images/j6b4qnxw7ufu/013pZkYwWwVUvuHrzPJ45U/c518446ab64f2926bd54441ded66de66/tv4_sport_live_4.png?fit=scale&w=256&fm=webp&q=75&h=256",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "usa": {
        "name": "USA",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/USA_Network_logo_%282016%29.svg/512px-USA_Network_logo_%282016%29.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "w9": {
        "name": "W9",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/fr/2/2b/W9_2012.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "zdf": {
        "name": "ZDF",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/ZDF_logo.svg/512px-ZDF_logo.svg.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "ziggosport": {
        "name": "ZIGGO SPORT",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/t6lerk1573988295.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "ziggosport2": {
        "name": "ZIGGO SPORT 2",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/l9v2ym1728725812.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "ziggosport3": {
        "name": "ZIGGO SPORT 3",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/8gk6uj1728725561.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "ziggosport4": {
        "name": "ZIGGO SPORT 4",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/ca0zut1728726639.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "ziggosport5": {
        "name": "ZIGGO SPORT 5",
        "thumbnail": "https://r2.thesportsdb.com/images/media/channel/logo/rj16081728726778.png",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
    "ziggosport6": {
        "name": "ZIGGO SPORT 6",
        "thumbnail": "https://www.dropbox.com/scl/fi/acxqcv09jv0gwc08jk3k7/ziggo_6.png?rlkey=m06y3z9byrnt3agrg1ygslkrv&st=09y8dbmf&dl=1",
        "fanart": "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
    },
}
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

def normalize_name(name):
    """Normalizza nome per matching (lowercase, no spazi, no caratteri speciali)"""
    return re.sub(r'[^a-z0-9]', '', name.lower())

def find_thumbnail(channel_name):
    """Cerca thumbnail nel dizionario hardcodato"""
    normalized = normalize_name(channel_name)
    channel_info = MANDRAKODI_CHANNELS.get(normalized)
    
    if channel_info:
        return {
            'name': channel_info['name'],
            'thumbnail': channel_info['thumbnail'],
            'fanart': channel_info['fanart']
        }
    return None

def extract_sansat_id(channel_info):
    """ID sansat dal link"""
    if isinstance(channel_info, dict):
        links = channel_info.get('links', [])
        if links:
            match = re.search(r'[?&]id=(\d+)', links[0])
            if match:
                return match.group(1)
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

def generate_country_jsons(events):
    """Crea JSON per ogni nazione con tutti i canali"""
    
    countries_dict = {}
    total_channels = 0
    thumbnails_matched = 0
    
    for match in events:
        team1 = match.get('team1', '')
        team2 = match.get('team2', '')
        league = match.get('league', '')
        sport = match.get('sport', 'Football')
        
        # Orario (+1 ora per Italia)
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
            channel_name = ch.get('name', '')
            channel_language = ch.get('language', '').upper()
            sansat_id = extract_sansat_id(ch)
            
            if sansat_id:
                # Paese del canale (per etichetta)
                channel_country_code = get_country_from_language(channel_language)
                channel_country_flag = f'[{channel_country_code}]' if channel_country_code else ''
                
                # Thumbnail dal dizionario hardcodato
                mk_match = find_thumbnail(channel_name)
                if mk_match:
                    thumbnail = mk_match['thumbnail']
                    fanart = mk_match['fanart']
                    thumbnails_matched += 1
                else:
                    thumbnail = "https://cdn-icons-png.flaticon.com/512/3524/3524659.png"
                    fanart = "https://www.stadiotardini.it/wp-content/uploads/2016/12/mandrakata.jpg"
                
                # Titolo
                if channel_language:
                    channel_display = f"{channel_name} {channel_country_flag}"
                else:
                    channel_display = channel_name
                
                title = f"[COLOR cyan][{time_str}][/COLOR] "
                title += f"[COLOR gold]{event_title}[/COLOR] - "
                title += channel_display
                
                info = f"{full_datetime} | {league} | {sport}"
                
                channel_item = {
                    "title": title,
                    "myresolve": f"sansat@@{sansat_id}",
                    "thumbnail": thumbnail,
                    "fanart": fanart,
                    "info": info,
                    "_timestamp": sort_timestamp
                }
                
                # Aggiungi alla nazione del CAMPIONATO
                if event_country_name not in countries_dict:
                    countries_dict[event_country_name] = []
                
                countries_dict[event_country_name].append(channel_item)
                total_channels += 1
    
    # Ordina per data
    for country in countries_dict:
        countries_dict[country].sort(key=lambda x: x['_timestamp'])
        for item in countries_dict[country]:
            del item['_timestamp']
    
    print(f"\nSTATISTICHE:")
    print(f"  Canali totali: {total_channels}")
    print(f"  Nazioni: {len(countries_dict)}")
    print(f"  Thumbnail trovate: {thumbnails_matched}/{total_channels}")
    
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
    print("GENERATORE EVENTI LIVE - VERSIONE HARDCODED")
    print("=" * 80)
    print(f"OK {len(MANDRAKODI_CHANNELS)} canali nel dizionario")
    print("OK Ogni evento nella nazione del suo campionato")
    print("OK Mostra TUTTI i canali (italiani + stranieri)")
    print()
    
    # 1. Eventi
    print("STEP 1: Download eventi sportivi")
    print("-" * 80)
    events = fetch_sports_events()
    
    if not events:
        print("Nessun evento trovato!")
        exit(1)
    
    # 2. Genera JSON
    print("\nSTEP 2: Organizzazione eventi")
    print("-" * 80)
    countries_dict = generate_country_jsons(events)
    
    if not countries_dict:
        print("Nessun canale disponibile!")
        exit(1)
    
    # 3. Salva
    print("\nSTEP 3: Salvataggio")
    print("-" * 80)
    save_all_jsons(countries_dict)
    
    print("\n" + "=" * 80)
    print("COMPLETATO!")
    print("=" * 80)
    print(f"\n{len(MANDRAKODI_CHANNELS)} canali disponibili per matching")
    print("\nESEMPIO ITALY:")
    print("  - Juventus vs Milan")
    print("    - DAZN 1 [IT]")
    print("    - Sky Sport [DE]")
    print("    - ESPN [ES]")
    print("    - beIN Sports [FR]")
