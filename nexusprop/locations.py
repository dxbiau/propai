"""
Australia Location Intelligence — All States & Territories.

Deep suburb-level market data powering the Location Scout, Deal Analysis,
and Value-Add Intelligence engines.

AUSTRALIAN PROPERTY ASSOCIATES — National Coverage

Coverage: 8 states · 50+ regions · 400+ suburbs · 15 data points per suburb
Including: auction clearance, days on market, vacancy, walkability,
council (LGA), gentrification stage, infrastructure pipeline
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# VIC_REGIONS: region → list of suburb dicts
# ---------------------------------------------------------------------------
# Each suburb dict fields:
#   name           — suburb name
#   postcode       — 4-digit postcode
#   median         — house median price AUD (backward compat key)
#   median_unit    — unit/apartment median (None if not applicable)
#   growth         — 12-month capital growth % (backward compat key)
#   yield          — gross rental yield houses % (backward compat key)
#   yield_unit     — gross rental yield units % (None if N/A)
#   pop            — population (backward compat key)
#   auction_clearance — auction clearance rate %
#   avg_dom        — average days on market
#   vacancy        — vacancy rate %
#   walkability    — walkability score 0-100
#   council        — Local Government Area name
#   gentrification — stage: early / emerging / established / mature / premium
#   infrastructure — notable upcoming project or None
# ---------------------------------------------------------------------------

VIC_REGIONS: dict[str, list[dict]] = {

    # ═══════════════════════════════════════════════════════════════
    # MELBOURNE METRO
    # ═══════════════════════════════════════════════════════════════

    "Melbourne — CBD & Inner City": [
        {"name": "Melbourne CBD", "postcode": "3000", "median": 1_100_000, "median_unit": 520_000, "growth": 1.8, "yield": 3.0, "yield_unit": 4.8, "pop": 55_000, "auction_clearance": 62, "avg_dom": 38, "vacancy": 3.2, "walkability": 98, "council": "Melbourne", "gentrification": "mature", "infrastructure": "Metro Tunnel Station 2025-26"},
        {"name": "Southbank", "postcode": "3006", "median": 950_000, "median_unit": 580_000, "growth": 1.5, "yield": 3.2, "yield_unit": 4.5, "pop": 22_000, "auction_clearance": 60, "avg_dom": 42, "vacancy": 3.5, "walkability": 95, "council": "Melbourne", "gentrification": "mature", "infrastructure": "Southbank Boulevard Renewal"},
        {"name": "Docklands", "postcode": "3008", "median": 880_000, "median_unit": 550_000, "growth": 2.0, "yield": 3.3, "yield_unit": 4.6, "pop": 18_000, "auction_clearance": 58, "avg_dom": 45, "vacancy": 3.8, "walkability": 90, "council": "Melbourne", "gentrification": "established", "infrastructure": "Harbour Esplanade Redevelopment"},
        {"name": "Carlton", "postcode": "3053", "median": 1_350_000, "median_unit": 480_000, "growth": 2.2, "yield": 2.8, "yield_unit": 4.5, "pop": 18_500, "auction_clearance": 68, "avg_dom": 32, "vacancy": 2.5, "walkability": 92, "council": "Melbourne", "gentrification": "mature", "infrastructure": None},
        {"name": "North Melbourne", "postcode": "3051", "median": 1_200_000, "median_unit": 460_000, "growth": 2.5, "yield": 3.0, "yield_unit": 4.6, "pop": 15_000, "auction_clearance": 66, "avg_dom": 30, "vacancy": 2.2, "walkability": 88, "council": "Melbourne", "gentrification": "established", "infrastructure": "Arden Station Metro Tunnel 2025"},
        {"name": "West Melbourne", "postcode": "3003", "median": 1_050_000, "median_unit": 490_000, "growth": 3.0, "yield": 3.1, "yield_unit": 4.5, "pop": 9_000, "auction_clearance": 64, "avg_dom": 33, "vacancy": 2.8, "walkability": 85, "council": "Melbourne", "gentrification": "emerging", "infrastructure": "West Melbourne Structure Plan"},
        {"name": "Parkville", "postcode": "3052", "median": 1_800_000, "median_unit": 520_000, "growth": 1.5, "yield": 2.5, "yield_unit": 4.0, "pop": 8_000, "auction_clearance": 72, "avg_dom": 28, "vacancy": 1.8, "walkability": 90, "council": "Melbourne", "gentrification": "premium", "infrastructure": "Parkville Station Metro Tunnel"},
        {"name": "East Melbourne", "postcode": "3002", "median": 2_500_000, "median_unit": 650_000, "growth": 1.2, "yield": 2.2, "yield_unit": 3.8, "pop": 5_500, "auction_clearance": 70, "avg_dom": 35, "vacancy": 1.5, "walkability": 92, "council": "Melbourne", "gentrification": "premium", "infrastructure": None},
    ],

    "Melbourne — Inner North": [
        {"name": "Fitzroy", "postcode": "3065", "median": 1_450_000, "median_unit": 560_000, "growth": 2.3, "yield": 2.7, "yield_unit": 4.2, "pop": 11_000, "auction_clearance": 73, "avg_dom": 26, "vacancy": 1.8, "walkability": 93, "council": "Yarra", "gentrification": "mature", "infrastructure": None},
        {"name": "Collingwood", "postcode": "3066", "median": 1_150_000, "median_unit": 510_000, "growth": 2.8, "yield": 3.0, "yield_unit": 4.5, "pop": 8_500, "auction_clearance": 71, "avg_dom": 27, "vacancy": 2.0, "walkability": 91, "council": "Yarra", "gentrification": "established", "infrastructure": "Smith Street Urban Renewal"},
        {"name": "Abbotsford", "postcode": "3067", "median": 1_250_000, "median_unit": 530_000, "growth": 2.5, "yield": 2.9, "yield_unit": 4.3, "pop": 8_000, "auction_clearance": 70, "avg_dom": 28, "vacancy": 1.7, "walkability": 86, "council": "Yarra", "gentrification": "established", "infrastructure": None},
        {"name": "Northcote", "postcode": "3070", "median": 1_300_000, "median_unit": 520_000, "growth": 3.0, "yield": 2.8, "yield_unit": 4.2, "pop": 14_000, "auction_clearance": 74, "avg_dom": 25, "vacancy": 1.5, "walkability": 84, "council": "Darebin", "gentrification": "mature", "infrastructure": None},
        {"name": "Thornbury", "postcode": "3071", "median": 1_150_000, "median_unit": 490_000, "growth": 3.5, "yield": 3.0, "yield_unit": 4.4, "pop": 18_000, "auction_clearance": 72, "avg_dom": 26, "vacancy": 1.6, "walkability": 78, "council": "Darebin", "gentrification": "established", "infrastructure": "High Street Activity Centre Plan"},
        {"name": "Preston", "postcode": "3072", "median": 950_000, "median_unit": 460_000, "growth": 4.2, "yield": 3.3, "yield_unit": 4.6, "pop": 33_000, "auction_clearance": 70, "avg_dom": 28, "vacancy": 1.8, "walkability": 72, "council": "Darebin", "gentrification": "established", "infrastructure": "Preston Market Redevelopment"},
        {"name": "Brunswick", "postcode": "3056", "median": 1_100_000, "median_unit": 480_000, "growth": 2.8, "yield": 3.0, "yield_unit": 4.5, "pop": 26_000, "auction_clearance": 72, "avg_dom": 25, "vacancy": 1.9, "walkability": 85, "council": "Merri-bek", "gentrification": "established", "infrastructure": "Brunswick Activity Centre"},
        {"name": "Coburg", "postcode": "3058", "median": 1_000_000, "median_unit": 470_000, "growth": 3.5, "yield": 3.1, "yield_unit": 4.5, "pop": 28_000, "auction_clearance": 70, "avg_dom": 27, "vacancy": 1.7, "walkability": 76, "council": "Merri-bek", "gentrification": "established", "infrastructure": "Upfield Corridor Level Crossing Removal"},
        {"name": "Pascoe Vale", "postcode": "3044", "median": 950_000, "median_unit": 440_000, "growth": 4.0, "yield": 3.2, "yield_unit": 4.6, "pop": 16_000, "auction_clearance": 68, "avg_dom": 29, "vacancy": 1.5, "walkability": 68, "council": "Merri-bek", "gentrification": "emerging", "infrastructure": None},
    ],

    "Melbourne — Inner East": [
        {"name": "Richmond", "postcode": "3121", "median": 1_350_000, "median_unit": 540_000, "growth": 2.2, "yield": 2.8, "yield_unit": 4.3, "pop": 28_000, "auction_clearance": 72, "avg_dom": 27, "vacancy": 2.0, "walkability": 90, "council": "Yarra", "gentrification": "mature", "infrastructure": "Cremorne Employment Precinct"},
        {"name": "Hawthorn", "postcode": "3122", "median": 2_200_000, "median_unit": 580_000, "growth": 1.6, "yield": 2.1, "yield_unit": 3.8, "pop": 23_000, "auction_clearance": 68, "avg_dom": 32, "vacancy": 1.5, "walkability": 82, "council": "Boroondara", "gentrification": "premium", "infrastructure": None},
        {"name": "Kew", "postcode": "3101", "median": 2_500_000, "median_unit": 610_000, "growth": 1.4, "yield": 1.9, "yield_unit": 3.6, "pop": 25_000, "auction_clearance": 66, "avg_dom": 34, "vacancy": 1.3, "walkability": 75, "council": "Boroondara", "gentrification": "premium", "infrastructure": None},
        {"name": "Camberwell", "postcode": "3124", "median": 2_450_000, "median_unit": 620_000, "growth": 1.5, "yield": 2.0, "yield_unit": 3.7, "pop": 22_000, "auction_clearance": 67, "avg_dom": 33, "vacancy": 1.2, "walkability": 78, "council": "Boroondara", "gentrification": "premium", "infrastructure": None},
        {"name": "Canterbury", "postcode": "3126", "median": 2_800_000, "median_unit": 700_000, "growth": 1.2, "yield": 1.8, "yield_unit": 3.5, "pop": 8_000, "auction_clearance": 65, "avg_dom": 36, "vacancy": 1.0, "walkability": 72, "council": "Boroondara", "gentrification": "premium", "infrastructure": None},
        {"name": "Balwyn", "postcode": "3103", "median": 2_100_000, "median_unit": 590_000, "growth": 1.8, "yield": 2.1, "yield_unit": 3.8, "pop": 14_000, "auction_clearance": 68, "avg_dom": 31, "vacancy": 1.1, "walkability": 70, "council": "Boroondara", "gentrification": "premium", "infrastructure": None},
        {"name": "Surrey Hills", "postcode": "3127", "median": 1_900_000, "median_unit": 580_000, "growth": 2.0, "yield": 2.3, "yield_unit": 3.9, "pop": 10_000, "auction_clearance": 70, "avg_dom": 30, "vacancy": 1.2, "walkability": 74, "council": "Whitehorse", "gentrification": "mature", "infrastructure": "Surrey Hills Level Crossing Removal"},
        {"name": "Box Hill", "postcode": "3128", "median": 1_250_000, "median_unit": 510_000, "growth": 2.8, "yield": 2.8, "yield_unit": 4.2, "pop": 12_000, "auction_clearance": 69, "avg_dom": 29, "vacancy": 1.8, "walkability": 80, "council": "Whitehorse", "gentrification": "established", "infrastructure": "Box Hill Metropolitan Activity Centre"},
    ],

    "Melbourne — Inner South": [
        {"name": "South Yarra", "postcode": "3141", "median": 1_550_000, "median_unit": 530_000, "growth": 1.8, "yield": 2.5, "yield_unit": 4.0, "pop": 24_000, "auction_clearance": 66, "avg_dom": 32, "vacancy": 2.5, "walkability": 92, "council": "Stonnington", "gentrification": "premium", "infrastructure": "South Yarra Station Upgrade"},
        {"name": "Prahran", "postcode": "3181", "median": 1_400_000, "median_unit": 500_000, "growth": 2.0, "yield": 2.6, "yield_unit": 4.2, "pop": 12_000, "auction_clearance": 68, "avg_dom": 30, "vacancy": 2.2, "walkability": 90, "council": "Stonnington", "gentrification": "mature", "infrastructure": None},
        {"name": "St Kilda", "postcode": "3182", "median": 1_300_000, "median_unit": 490_000, "growth": 2.5, "yield": 2.8, "yield_unit": 4.5, "pop": 20_000, "auction_clearance": 65, "avg_dom": 31, "vacancy": 2.8, "walkability": 92, "council": "Port Phillip", "gentrification": "mature", "infrastructure": "St Kilda Junction Improvement"},
        {"name": "Windsor", "postcode": "3181", "median": 1_200_000, "median_unit": 480_000, "growth": 2.8, "yield": 2.9, "yield_unit": 4.4, "pop": 8_000, "auction_clearance": 67, "avg_dom": 28, "vacancy": 2.0, "walkability": 88, "council": "Stonnington", "gentrification": "established", "infrastructure": None},
        {"name": "Albert Park", "postcode": "3206", "median": 2_000_000, "median_unit": 620_000, "growth": 1.5, "yield": 2.2, "yield_unit": 3.5, "pop": 6_500, "auction_clearance": 70, "avg_dom": 30, "vacancy": 1.5, "walkability": 88, "council": "Port Phillip", "gentrification": "premium", "infrastructure": None},
        {"name": "South Melbourne", "postcode": "3205", "median": 1_500_000, "median_unit": 550_000, "growth": 2.2, "yield": 2.5, "yield_unit": 4.0, "pop": 11_000, "auction_clearance": 68, "avg_dom": 29, "vacancy": 2.0, "walkability": 90, "council": "Port Phillip", "gentrification": "mature", "infrastructure": "Fishermans Bend Urban Renewal"},
        {"name": "Port Melbourne", "postcode": "3207", "median": 1_400_000, "median_unit": 600_000, "growth": 2.0, "yield": 2.6, "yield_unit": 3.8, "pop": 17_000, "auction_clearance": 66, "avg_dom": 33, "vacancy": 2.2, "walkability": 85, "council": "Port Phillip", "gentrification": "mature", "infrastructure": "Fishermans Bend Tram Extension"},
        {"name": "Elwood", "postcode": "3184", "median": 1_600_000, "median_unit": 550_000, "growth": 1.8, "yield": 2.4, "yield_unit": 3.8, "pop": 14_000, "auction_clearance": 67, "avg_dom": 32, "vacancy": 1.8, "walkability": 84, "council": "Port Phillip", "gentrification": "mature", "infrastructure": None},
    ],

    "Melbourne — Inner West": [
        {"name": "Footscray", "postcode": "3011", "median": 870_000, "median_unit": 420_000, "growth": 4.5, "yield": 3.5, "yield_unit": 5.0, "pop": 18_000, "auction_clearance": 69, "avg_dom": 27, "vacancy": 1.8, "walkability": 82, "council": "Maribyrnong", "gentrification": "emerging", "infrastructure": "Footscray Hospital Redevelopment, West Gate Tunnel completion 2025"},
        {"name": "Seddon", "postcode": "3011", "median": 1_050_000, "median_unit": 480_000, "growth": 3.8, "yield": 3.0, "yield_unit": 4.5, "pop": 6_000, "auction_clearance": 72, "avg_dom": 24, "vacancy": 1.5, "walkability": 80, "council": "Maribyrnong", "gentrification": "established", "infrastructure": None},
        {"name": "Yarraville", "postcode": "3013", "median": 1_100_000, "median_unit": 490_000, "growth": 3.5, "yield": 2.9, "yield_unit": 4.3, "pop": 15_000, "auction_clearance": 73, "avg_dom": 25, "vacancy": 1.4, "walkability": 78, "council": "Maribyrnong", "gentrification": "established", "infrastructure": "West Gate Tunnel Project 2025"},
        {"name": "Williamstown", "postcode": "3016", "median": 1_350_000, "median_unit": 550_000, "growth": 2.5, "yield": 2.6, "yield_unit": 3.8, "pop": 14_000, "auction_clearance": 70, "avg_dom": 28, "vacancy": 1.3, "walkability": 75, "council": "Hobsons Bay", "gentrification": "mature", "infrastructure": None},
        {"name": "Newport", "postcode": "3015", "median": 1_000_000, "median_unit": 460_000, "growth": 3.5, "yield": 3.1, "yield_unit": 4.5, "pop": 12_000, "auction_clearance": 71, "avg_dom": 26, "vacancy": 1.5, "walkability": 72, "council": "Hobsons Bay", "gentrification": "established", "infrastructure": "Newport Station Precinct Uplift"},
        {"name": "Kingsville", "postcode": "3012", "median": 950_000, "median_unit": 440_000, "growth": 4.0, "yield": 3.2, "yield_unit": 4.6, "pop": 5_000, "auction_clearance": 70, "avg_dom": 25, "vacancy": 1.6, "walkability": 76, "council": "Maribyrnong", "gentrification": "emerging", "infrastructure": None},
        {"name": "Maidstone", "postcode": "3012", "median": 820_000, "median_unit": 400_000, "growth": 4.8, "yield": 3.5, "yield_unit": 5.0, "pop": 7_500, "auction_clearance": 66, "avg_dom": 28, "vacancy": 1.9, "walkability": 70, "council": "Maribyrnong", "gentrification": "early", "infrastructure": "Maribyrnong Defence Site Redevelopment"},
        {"name": "Maribyrnong", "postcode": "3032", "median": 900_000, "median_unit": 430_000, "growth": 4.2, "yield": 3.3, "yield_unit": 4.8, "pop": 12_000, "auction_clearance": 68, "avg_dom": 27, "vacancy": 1.7, "walkability": 74, "council": "Maribyrnong", "gentrification": "emerging", "infrastructure": "Highpoint Activity Centre Expansion"},
    ],

    "Melbourne — Western Growth": [
        {"name": "Werribee", "postcode": "3030", "median": 560_000, "median_unit": 380_000, "growth": 5.2, "yield": 4.5, "yield_unit": 5.5, "pop": 42_000, "auction_clearance": 58, "avg_dom": 35, "vacancy": 1.8, "walkability": 55, "council": "Wyndham", "gentrification": "emerging", "infrastructure": "Werribee Employment Precinct P15B"},
        {"name": "Hoppers Crossing", "postcode": "3029", "median": 580_000, "median_unit": 370_000, "growth": 4.8, "yield": 4.3, "yield_unit": 5.4, "pop": 34_000, "auction_clearance": 57, "avg_dom": 36, "vacancy": 1.9, "walkability": 50, "council": "Wyndham", "gentrification": "established", "infrastructure": None},
        {"name": "Point Cook", "postcode": "3030", "median": 680_000, "median_unit": 420_000, "growth": 4.5, "yield": 4.0, "yield_unit": 5.0, "pop": 65_000, "auction_clearance": 61, "avg_dom": 32, "vacancy": 1.5, "walkability": 48, "council": "Wyndham", "gentrification": "established", "infrastructure": "Point Cook South Employment Zone"},
        {"name": "Tarneit", "postcode": "3029", "median": 580_000, "median_unit": 370_000, "growth": 5.5, "yield": 4.5, "yield_unit": 5.5, "pop": 55_000, "auction_clearance": 56, "avg_dom": 38, "vacancy": 2.0, "walkability": 42, "council": "Wyndham", "gentrification": "early", "infrastructure": "Tarneit West PSP Development"},
        {"name": "Truganina", "postcode": "3029", "median": 560_000, "median_unit": 350_000, "growth": 5.8, "yield": 4.6, "yield_unit": 5.6, "pop": 35_000, "auction_clearance": 55, "avg_dom": 40, "vacancy": 2.1, "walkability": 38, "council": "Wyndham", "gentrification": "early", "infrastructure": "Western Intermodal Freight Terminal"},
        {"name": "Melton", "postcode": "3337", "median": 490_000, "median_unit": 340_000, "growth": 5.5, "yield": 4.8, "yield_unit": 5.8, "pop": 62_000, "auction_clearance": 54, "avg_dom": 42, "vacancy": 2.0, "walkability": 45, "council": "Melton", "gentrification": "early", "infrastructure": "Melton Rail Electrification 2028"},
        {"name": "Caroline Springs", "postcode": "3023", "median": 620_000, "median_unit": 390_000, "growth": 4.5, "yield": 4.2, "yield_unit": 5.2, "pop": 28_000, "auction_clearance": 59, "avg_dom": 34, "vacancy": 1.7, "walkability": 52, "council": "Melton", "gentrification": "established", "infrastructure": None},
        {"name": "Sunshine", "postcode": "3020", "median": 720_000, "median_unit": 400_000, "growth": 4.5, "yield": 3.8, "yield_unit": 5.0, "pop": 10_000, "auction_clearance": 63, "avg_dom": 30, "vacancy": 1.8, "walkability": 72, "council": "Brimbank", "gentrification": "emerging", "infrastructure": "Sunshine Super Hub — Metro Tunnel + Airport Rail"},
        {"name": "St Albans", "postcode": "3021", "median": 620_000, "median_unit": 380_000, "growth": 5.0, "yield": 4.2, "yield_unit": 5.3, "pop": 38_000, "auction_clearance": 60, "avg_dom": 33, "vacancy": 1.9, "walkability": 62, "council": "Brimbank", "gentrification": "early", "infrastructure": "St Albans Level Crossing Removal Complete"},
    ],

    "Melbourne — Northern Growth": [
        {"name": "Craigieburn", "postcode": "3064", "median": 570_000, "median_unit": 380_000, "growth": 5.2, "yield": 4.3, "yield_unit": 5.4, "pop": 58_000, "auction_clearance": 56, "avg_dom": 38, "vacancy": 1.8, "walkability": 40, "council": "Hume", "gentrification": "established", "infrastructure": "Craigieburn South Employment PSP"},
        {"name": "Broadmeadows", "postcode": "3047", "median": 540_000, "median_unit": 350_000, "growth": 5.5, "yield": 4.5, "yield_unit": 5.6, "pop": 15_000, "auction_clearance": 55, "avg_dom": 40, "vacancy": 2.0, "walkability": 58, "council": "Hume", "gentrification": "early", "infrastructure": "Broadmeadows Metropolitan Activity Centre"},
        {"name": "Epping", "postcode": "3076", "median": 610_000, "median_unit": 390_000, "growth": 4.8, "yield": 4.2, "yield_unit": 5.3, "pop": 36_000, "auction_clearance": 58, "avg_dom": 36, "vacancy": 1.7, "walkability": 48, "council": "Whittlesea", "gentrification": "established", "infrastructure": "Epping North East PSP"},
        {"name": "South Morang", "postcode": "3752", "median": 640_000, "median_unit": 400_000, "growth": 4.5, "yield": 4.0, "yield_unit": 5.2, "pop": 35_000, "auction_clearance": 59, "avg_dom": 35, "vacancy": 1.6, "walkability": 42, "council": "Whittlesea", "gentrification": "established", "infrastructure": "South Morang Rail Extension Completed"},
        {"name": "Doreen", "postcode": "3754", "median": 650_000, "median_unit": None, "growth": 4.2, "yield": 3.9, "yield_unit": None, "pop": 32_000, "auction_clearance": 58, "avg_dom": 36, "vacancy": 1.5, "walkability": 35, "council": "Whittlesea", "gentrification": "established", "infrastructure": None},
        {"name": "Mernda", "postcode": "3754", "median": 600_000, "median_unit": None, "growth": 4.8, "yield": 4.2, "yield_unit": None, "pop": 25_000, "auction_clearance": 57, "avg_dom": 37, "vacancy": 1.6, "walkability": 38, "council": "Whittlesea", "gentrification": "early", "infrastructure": "Mernda Town Centre Development"},
        {"name": "Mill Park", "postcode": "3082", "median": 620_000, "median_unit": 380_000, "growth": 4.5, "yield": 4.1, "yield_unit": 5.2, "pop": 30_000, "auction_clearance": 58, "avg_dom": 35, "vacancy": 1.7, "walkability": 45, "council": "Whittlesea", "gentrification": "established", "infrastructure": None},
        {"name": "Thomastown", "postcode": "3074", "median": 600_000, "median_unit": 370_000, "growth": 5.0, "yield": 4.2, "yield_unit": 5.4, "pop": 22_000, "auction_clearance": 57, "avg_dom": 36, "vacancy": 1.8, "walkability": 52, "council": "Whittlesea", "gentrification": "established", "infrastructure": None},
        {"name": "Lalor", "postcode": "3075", "median": 580_000, "median_unit": 360_000, "growth": 5.2, "yield": 4.3, "yield_unit": 5.5, "pop": 24_000, "auction_clearance": 56, "avg_dom": 37, "vacancy": 1.9, "walkability": 50, "council": "Whittlesea", "gentrification": "early", "infrastructure": None},
    ],

    "Melbourne — Eastern Suburbs": [
        {"name": "Doncaster", "postcode": "3108", "median": 1_350_000, "median_unit": 560_000, "growth": 2.5, "yield": 2.7, "yield_unit": 4.0, "pop": 21_000, "auction_clearance": 67, "avg_dom": 30, "vacancy": 1.3, "walkability": 60, "council": "Manningham", "gentrification": "mature", "infrastructure": "Doncaster Busway Upgrade"},
        {"name": "Ringwood", "postcode": "3134", "median": 950_000, "median_unit": 480_000, "growth": 3.5, "yield": 3.2, "yield_unit": 4.5, "pop": 18_000, "auction_clearance": 65, "avg_dom": 31, "vacancy": 1.5, "walkability": 68, "council": "Maroondah", "gentrification": "established", "infrastructure": "Ringwood MAC Redevelopment"},
        {"name": "Croydon", "postcode": "3136", "median": 820_000, "median_unit": 450_000, "growth": 4.0, "yield": 3.5, "yield_unit": 4.8, "pop": 25_000, "auction_clearance": 63, "avg_dom": 33, "vacancy": 1.6, "walkability": 60, "council": "Maroondah", "gentrification": "established", "infrastructure": None},
        {"name": "Lilydale", "postcode": "3140", "median": 750_000, "median_unit": 430_000, "growth": 4.5, "yield": 3.8, "yield_unit": 5.0, "pop": 17_000, "auction_clearance": 61, "avg_dom": 35, "vacancy": 1.7, "walkability": 55, "council": "Yarra Ranges", "gentrification": "established", "infrastructure": "Lilydale Quarry Redevelopment"},
        {"name": "Mitcham", "postcode": "3132", "median": 1_050_000, "median_unit": 500_000, "growth": 3.0, "yield": 3.0, "yield_unit": 4.3, "pop": 14_000, "auction_clearance": 66, "avg_dom": 30, "vacancy": 1.4, "walkability": 62, "council": "Whitehorse", "gentrification": "mature", "infrastructure": None},
        {"name": "Nunawading", "postcode": "3131", "median": 1_100_000, "median_unit": 510_000, "growth": 2.8, "yield": 2.9, "yield_unit": 4.2, "pop": 12_000, "auction_clearance": 67, "avg_dom": 29, "vacancy": 1.3, "walkability": 65, "council": "Whitehorse", "gentrification": "mature", "infrastructure": None},
        {"name": "Blackburn", "postcode": "3130", "median": 1_300_000, "median_unit": 540_000, "growth": 2.5, "yield": 2.6, "yield_unit": 4.0, "pop": 13_000, "auction_clearance": 68, "avg_dom": 29, "vacancy": 1.2, "walkability": 64, "council": "Whitehorse", "gentrification": "mature", "infrastructure": None},
        {"name": "Bayswater", "postcode": "3153", "median": 780_000, "median_unit": 430_000, "growth": 4.2, "yield": 3.6, "yield_unit": 4.8, "pop": 11_000, "auction_clearance": 62, "avg_dom": 33, "vacancy": 1.6, "walkability": 55, "council": "Knox", "gentrification": "established", "infrastructure": "Bayswater Level Crossing Removal"},
        {"name": "Boronia", "postcode": "3155", "median": 750_000, "median_unit": 420_000, "growth": 4.5, "yield": 3.8, "yield_unit": 5.0, "pop": 22_000, "auction_clearance": 61, "avg_dom": 34, "vacancy": 1.7, "walkability": 58, "council": "Knox", "gentrification": "established", "infrastructure": None},
    ],

    "Melbourne — South Eastern": [
        {"name": "Dandenong", "postcode": "3175", "median": 600_000, "median_unit": 380_000, "growth": 5.0, "yield": 4.5, "yield_unit": 5.5, "pop": 30_000, "auction_clearance": 58, "avg_dom": 35, "vacancy": 1.8, "walkability": 65, "council": "Greater Dandenong", "gentrification": "early", "infrastructure": "Revitalising Central Dandenong"},
        {"name": "Noble Park", "postcode": "3174", "median": 650_000, "median_unit": 400_000, "growth": 4.8, "yield": 4.2, "yield_unit": 5.3, "pop": 33_000, "auction_clearance": 57, "avg_dom": 36, "vacancy": 1.9, "walkability": 58, "council": "Greater Dandenong", "gentrification": "early", "infrastructure": "Noble Park MAC Revitalisation"},
        {"name": "Springvale", "postcode": "3171", "median": 680_000, "median_unit": 410_000, "growth": 4.5, "yield": 4.0, "yield_unit": 5.2, "pop": 22_000, "auction_clearance": 59, "avg_dom": 34, "vacancy": 1.7, "walkability": 62, "council": "Greater Dandenong", "gentrification": "emerging", "infrastructure": "Springvale Activity Centre Plan"},
        {"name": "Cranbourne", "postcode": "3977", "median": 600_000, "median_unit": 380_000, "growth": 5.5, "yield": 4.5, "yield_unit": 5.6, "pop": 45_000, "auction_clearance": 56, "avg_dom": 38, "vacancy": 1.8, "walkability": 45, "council": "Casey", "gentrification": "established", "infrastructure": "Cranbourne Line Level Crossing Removals"},
        {"name": "Berwick", "postcode": "3806", "median": 700_000, "median_unit": 430_000, "growth": 4.2, "yield": 3.8, "yield_unit": 5.0, "pop": 48_000, "auction_clearance": 60, "avg_dom": 33, "vacancy": 1.5, "walkability": 50, "council": "Casey", "gentrification": "established", "infrastructure": None},
        {"name": "Narre Warren", "postcode": "3805", "median": 650_000, "median_unit": 410_000, "growth": 4.5, "yield": 4.0, "yield_unit": 5.2, "pop": 35_000, "auction_clearance": 58, "avg_dom": 35, "vacancy": 1.7, "walkability": 48, "council": "Casey", "gentrification": "established", "infrastructure": "Narre Warren Fountain Gate MAC"},
        {"name": "Pakenham", "postcode": "3810", "median": 560_000, "median_unit": 370_000, "growth": 5.8, "yield": 4.6, "yield_unit": 5.5, "pop": 50_000, "auction_clearance": 55, "avg_dom": 40, "vacancy": 2.0, "walkability": 42, "council": "Cardinia", "gentrification": "early", "infrastructure": "Pakenham East PSP Development"},
        {"name": "Officer", "postcode": "3809", "median": 600_000, "median_unit": 390_000, "growth": 5.5, "yield": 4.3, "yield_unit": 5.4, "pop": 20_000, "auction_clearance": 57, "avg_dom": 38, "vacancy": 1.8, "walkability": 40, "council": "Cardinia", "gentrification": "early", "infrastructure": "Officer Town Centre Development"},
        {"name": "Clyde", "postcode": "3978", "median": 580_000, "median_unit": None, "growth": 6.0, "yield": 4.5, "yield_unit": None, "pop": 15_000, "auction_clearance": 55, "avg_dom": 42, "vacancy": 2.1, "walkability": 35, "council": "Casey", "gentrification": "early", "infrastructure": "Clyde South PSP — 30,000 new homes planned"},
    ],

    "Melbourne — Bayside & Peninsula": [
        {"name": "Brighton", "postcode": "3186", "median": 2_800_000, "median_unit": 700_000, "growth": 1.5, "yield": 1.8, "yield_unit": 3.5, "pop": 22_000, "auction_clearance": 65, "avg_dom": 35, "vacancy": 1.2, "walkability": 72, "council": "Bayside", "gentrification": "premium", "infrastructure": None},
        {"name": "Hampton", "postcode": "3188", "median": 2_100_000, "median_unit": 620_000, "growth": 1.8, "yield": 2.0, "yield_unit": 3.7, "pop": 13_000, "auction_clearance": 66, "avg_dom": 33, "vacancy": 1.3, "walkability": 70, "council": "Bayside", "gentrification": "premium", "infrastructure": None},
        {"name": "Cheltenham", "postcode": "3192", "median": 1_200_000, "median_unit": 520_000, "growth": 3.0, "yield": 2.8, "yield_unit": 4.2, "pop": 21_000, "auction_clearance": 67, "avg_dom": 30, "vacancy": 1.4, "walkability": 65, "council": "Kingston", "gentrification": "mature", "infrastructure": "Cheltenham-Mentone Level Crossing Removal"},
        {"name": "Mentone", "postcode": "3194", "median": 1_300_000, "median_unit": 540_000, "growth": 2.8, "yield": 2.7, "yield_unit": 4.0, "pop": 12_000, "auction_clearance": 66, "avg_dom": 31, "vacancy": 1.3, "walkability": 68, "council": "Kingston", "gentrification": "mature", "infrastructure": None},
        {"name": "Frankston", "postcode": "3199", "median": 720_000, "median_unit": 420_000, "growth": 4.5, "yield": 3.8, "yield_unit": 5.0, "pop": 36_000, "auction_clearance": 60, "avg_dom": 33, "vacancy": 1.8, "walkability": 65, "council": "Frankston", "gentrification": "emerging", "infrastructure": "Frankston MAC + Health & Education Precinct"},
        {"name": "Mornington", "postcode": "3931", "median": 880_000, "median_unit": 500_000, "growth": 3.5, "yield": 3.2, "yield_unit": 4.5, "pop": 24_000, "auction_clearance": 62, "avg_dom": 34, "vacancy": 1.5, "walkability": 60, "council": "Mornington Peninsula", "gentrification": "mature", "infrastructure": None},
        {"name": "Sorrento", "postcode": "3943", "median": 1_500_000, "median_unit": 650_000, "growth": 2.0, "yield": 2.5, "yield_unit": 3.8, "pop": 2_800, "auction_clearance": 58, "avg_dom": 40, "vacancy": 3.0, "walkability": 55, "council": "Mornington Peninsula", "gentrification": "premium", "infrastructure": None},
        {"name": "Dromana", "postcode": "3936", "median": 780_000, "median_unit": 480_000, "growth": 3.8, "yield": 3.5, "yield_unit": 4.8, "pop": 6_500, "auction_clearance": 59, "avg_dom": 36, "vacancy": 2.5, "walkability": 50, "council": "Mornington Peninsula", "gentrification": "established", "infrastructure": None},
        {"name": "Rosebud", "postcode": "3939", "median": 680_000, "median_unit": 440_000, "growth": 4.0, "yield": 3.8, "yield_unit": 5.0, "pop": 15_000, "auction_clearance": 57, "avg_dom": 38, "vacancy": 2.8, "walkability": 52, "council": "Mornington Peninsula", "gentrification": "established", "infrastructure": None},
    ],

    # ═══════════════════════════════════════════════════════════════
    # REGIONAL VIC
    # ═══════════════════════════════════════════════════════════════

    "Geelong & Surf Coast": [
        {"name": "Geelong", "postcode": "3220", "median": 690_000, "median_unit": 420_000, "growth": 4.2, "yield": 4.0, "yield_unit": 5.2, "pop": 195_000, "auction_clearance": 62, "avg_dom": 32, "vacancy": 1.8, "walkability": 70, "council": "Greater Geelong", "gentrification": "established", "infrastructure": "Geelong City Deal — $370M transformation"},
        {"name": "Newtown", "postcode": "3220", "median": 850_000, "median_unit": 480_000, "growth": 3.5, "yield": 3.5, "yield_unit": 4.5, "pop": 10_000, "auction_clearance": 65, "avg_dom": 28, "vacancy": 1.5, "walkability": 75, "council": "Greater Geelong", "gentrification": "mature", "infrastructure": None},
        {"name": "Belmont", "postcode": "3216", "median": 640_000, "median_unit": 400_000, "growth": 4.5, "yield": 4.2, "yield_unit": 5.3, "pop": 14_000, "auction_clearance": 61, "avg_dom": 33, "vacancy": 1.7, "walkability": 65, "council": "Greater Geelong", "gentrification": "established", "infrastructure": None},
        {"name": "Corio", "postcode": "3214", "median": 460_000, "median_unit": 320_000, "growth": 6.0, "yield": 5.2, "yield_unit": 6.0, "pop": 20_000, "auction_clearance": 55, "avg_dom": 38, "vacancy": 2.2, "walkability": 48, "council": "Greater Geelong", "gentrification": "early", "infrastructure": "Northern Geelong Growth Area Plan"},
        {"name": "Norlane", "postcode": "3214", "median": 420_000, "median_unit": 300_000, "growth": 6.5, "yield": 5.5, "yield_unit": 6.2, "pop": 10_500, "auction_clearance": 53, "avg_dom": 40, "vacancy": 2.5, "walkability": 45, "council": "Greater Geelong", "gentrification": "early", "infrastructure": "Norlane Community Renewal Program"},
        {"name": "Lara", "postcode": "3212", "median": 590_000, "median_unit": 380_000, "growth": 5.0, "yield": 4.5, "yield_unit": 5.5, "pop": 24_000, "auction_clearance": 59, "avg_dom": 34, "vacancy": 1.6, "walkability": 50, "council": "Greater Geelong", "gentrification": "established", "infrastructure": "Lara Growth Area PSP"},
        {"name": "Ocean Grove", "postcode": "3226", "median": 780_000, "median_unit": 480_000, "growth": 3.8, "yield": 3.5, "yield_unit": 4.5, "pop": 16_000, "auction_clearance": 60, "avg_dom": 35, "vacancy": 2.0, "walkability": 55, "council": "Greater Geelong", "gentrification": "mature", "infrastructure": None},
        {"name": "Torquay", "postcode": "3228", "median": 900_000, "median_unit": 520_000, "growth": 3.5, "yield": 3.2, "yield_unit": 4.2, "pop": 18_000, "auction_clearance": 58, "avg_dom": 36, "vacancy": 2.5, "walkability": 52, "council": "Surf Coast", "gentrification": "mature", "infrastructure": None},
        {"name": "Armstrong Creek", "postcode": "3217", "median": 620_000, "median_unit": None, "growth": 5.5, "yield": 4.2, "yield_unit": None, "pop": 20_000, "auction_clearance": 57, "avg_dom": 37, "vacancy": 1.5, "walkability": 42, "council": "Greater Geelong", "gentrification": "early", "infrastructure": "Armstrong Creek Town Centre — 70,000 residents planned"},
    ],

    "Bendigo & Goldfields": [
        {"name": "Bendigo", "postcode": "3550", "median": 530_000, "median_unit": 340_000, "growth": 4.0, "yield": 4.5, "yield_unit": 5.5, "pop": 100_000, "auction_clearance": 58, "avg_dom": 35, "vacancy": 1.8, "walkability": 68, "council": "Greater Bendigo", "gentrification": "established", "infrastructure": "Bendigo Hospital Expansion + GovHub"},
        {"name": "Quarry Hill", "postcode": "3550", "median": 490_000, "median_unit": 320_000, "growth": 4.2, "yield": 4.7, "yield_unit": 5.7, "pop": 3_000, "auction_clearance": 57, "avg_dom": 36, "vacancy": 1.9, "walkability": 65, "council": "Greater Bendigo", "gentrification": "emerging", "infrastructure": None},
        {"name": "Epsom", "postcode": "3551", "median": 510_000, "median_unit": 340_000, "growth": 4.5, "yield": 4.4, "yield_unit": 5.4, "pop": 9_000, "auction_clearance": 56, "avg_dom": 37, "vacancy": 1.7, "walkability": 50, "council": "Greater Bendigo", "gentrification": "established", "infrastructure": "Epsom Employment Precinct"},
        {"name": "Kangaroo Flat", "postcode": "3555", "median": 430_000, "median_unit": 290_000, "growth": 5.0, "yield": 5.0, "yield_unit": 5.8, "pop": 10_000, "auction_clearance": 55, "avg_dom": 38, "vacancy": 2.0, "walkability": 55, "council": "Greater Bendigo", "gentrification": "emerging", "infrastructure": None},
        {"name": "Strathdale", "postcode": "3550", "median": 560_000, "median_unit": None, "growth": 3.5, "yield": 4.0, "yield_unit": None, "pop": 5_500, "auction_clearance": 59, "avg_dom": 34, "vacancy": 1.5, "walkability": 58, "council": "Greater Bendigo", "gentrification": "established", "infrastructure": None},
        {"name": "Golden Square", "postcode": "3555", "median": 440_000, "median_unit": 300_000, "growth": 4.8, "yield": 4.8, "yield_unit": 5.8, "pop": 6_500, "auction_clearance": 56, "avg_dom": 37, "vacancy": 1.8, "walkability": 60, "council": "Greater Bendigo", "gentrification": "emerging", "infrastructure": None},
        {"name": "Eaglehawk", "postcode": "3556", "median": 410_000, "median_unit": 280_000, "growth": 5.2, "yield": 5.2, "yield_unit": 6.0, "pop": 5_000, "auction_clearance": 54, "avg_dom": 39, "vacancy": 2.0, "walkability": 52, "council": "Greater Bendigo", "gentrification": "early", "infrastructure": None},
        {"name": "Castlemaine", "postcode": "3450", "median": 550_000, "median_unit": 350_000, "growth": 3.8, "yield": 4.0, "yield_unit": 5.0, "pop": 9_000, "auction_clearance": 55, "avg_dom": 40, "vacancy": 1.8, "walkability": 62, "council": "Mount Alexander", "gentrification": "established", "infrastructure": "Castlemaine Heritage Town Revival"},
    ],

    "Ballarat & Central Highlands": [
        {"name": "Ballarat", "postcode": "3350", "median": 490_000, "median_unit": 310_000, "growth": 4.5, "yield": 4.5, "yield_unit": 5.5, "pop": 110_000, "auction_clearance": 56, "avg_dom": 37, "vacancy": 2.0, "walkability": 65, "council": "Ballarat", "gentrification": "established", "infrastructure": "Ballarat GovHub + Station Precinct"},
        {"name": "Sebastopol", "postcode": "3356", "median": 410_000, "median_unit": 280_000, "growth": 5.0, "yield": 5.0, "yield_unit": 5.8, "pop": 9_000, "auction_clearance": 54, "avg_dom": 39, "vacancy": 2.2, "walkability": 55, "council": "Ballarat", "gentrification": "emerging", "infrastructure": None},
        {"name": "Wendouree", "postcode": "3355", "median": 430_000, "median_unit": 290_000, "growth": 4.8, "yield": 4.8, "yield_unit": 5.6, "pop": 8_000, "auction_clearance": 55, "avg_dom": 38, "vacancy": 2.0, "walkability": 58, "council": "Ballarat", "gentrification": "established", "infrastructure": None},
        {"name": "Alfredton", "postcode": "3350", "median": 520_000, "median_unit": None, "growth": 4.2, "yield": 4.2, "yield_unit": None, "pop": 10_000, "auction_clearance": 57, "avg_dom": 36, "vacancy": 1.8, "walkability": 50, "council": "Ballarat", "gentrification": "established", "infrastructure": "Alfredton South Growth Area"},
        {"name": "Buninyong", "postcode": "3357", "median": 580_000, "median_unit": None, "growth": 3.5, "yield": 3.8, "yield_unit": None, "pop": 4_000, "auction_clearance": 55, "avg_dom": 40, "vacancy": 1.5, "walkability": 45, "council": "Ballarat", "gentrification": "established", "infrastructure": None},
        {"name": "Delacombe", "postcode": "3356", "median": 420_000, "median_unit": None, "growth": 5.5, "yield": 4.8, "yield_unit": None, "pop": 8_000, "auction_clearance": 53, "avg_dom": 40, "vacancy": 2.2, "walkability": 42, "council": "Ballarat", "gentrification": "early", "infrastructure": "Delacombe Town Centre Development"},
        {"name": "Brown Hill", "postcode": "3350", "median": 470_000, "median_unit": None, "growth": 4.5, "yield": 4.5, "yield_unit": None, "pop": 3_500, "auction_clearance": 55, "avg_dom": 38, "vacancy": 1.8, "walkability": 48, "council": "Ballarat", "gentrification": "emerging", "infrastructure": None},
    ],

    "Gippsland": [
        {"name": "Traralgon", "postcode": "3844", "median": 380_000, "median_unit": 250_000, "growth": 4.0, "yield": 5.2, "yield_unit": 6.0, "pop": 27_000, "auction_clearance": 52, "avg_dom": 42, "vacancy": 2.2, "walkability": 55, "council": "Latrobe", "gentrification": "established", "infrastructure": "Gippsland Logistics Precinct + SEC Revival"},
        {"name": "Morwell", "postcode": "3840", "median": 280_000, "median_unit": 200_000, "growth": 5.0, "yield": 6.5, "yield_unit": 7.5, "pop": 14_000, "auction_clearance": 48, "avg_dom": 48, "vacancy": 3.0, "walkability": 52, "council": "Latrobe", "gentrification": "early", "infrastructure": "Latrobe Valley Authority Transition"},
        {"name": "Sale", "postcode": "3850", "median": 400_000, "median_unit": 280_000, "growth": 3.8, "yield": 5.0, "yield_unit": 5.8, "pop": 15_000, "auction_clearance": 50, "avg_dom": 44, "vacancy": 2.0, "walkability": 58, "council": "Wellington", "gentrification": "established", "infrastructure": "Port of Sale Revitalisation"},
        {"name": "Warragul", "postcode": "3820", "median": 530_000, "median_unit": 350_000, "growth": 4.5, "yield": 4.2, "yield_unit": 5.2, "pop": 16_000, "auction_clearance": 56, "avg_dom": 36, "vacancy": 1.6, "walkability": 58, "council": "Baw Baw", "gentrification": "established", "infrastructure": "Warragul-Drouin Growth Corridor"},
        {"name": "Drouin", "postcode": "3818", "median": 480_000, "median_unit": 320_000, "growth": 5.0, "yield": 4.5, "yield_unit": 5.5, "pop": 14_000, "auction_clearance": 55, "avg_dom": 37, "vacancy": 1.8, "walkability": 52, "council": "Baw Baw", "gentrification": "emerging", "infrastructure": None},
        {"name": "Bairnsdale", "postcode": "3875", "median": 420_000, "median_unit": 290_000, "growth": 3.5, "yield": 4.8, "yield_unit": 5.8, "pop": 15_000, "auction_clearance": 50, "avg_dom": 45, "vacancy": 2.2, "walkability": 52, "council": "East Gippsland", "gentrification": "established", "infrastructure": None},
        {"name": "Wonthaggi", "postcode": "3995", "median": 470_000, "median_unit": 320_000, "growth": 4.5, "yield": 4.5, "yield_unit": 5.5, "pop": 8_000, "auction_clearance": 53, "avg_dom": 40, "vacancy": 2.0, "walkability": 50, "council": "Bass Coast", "gentrification": "emerging", "infrastructure": "Victorian Desalination Plant (existing), Bass Coast tourism growth"},
    ],

    "Hume & North East VIC": [
        {"name": "Shepparton", "postcode": "3630", "median": 390_000, "median_unit": 260_000, "growth": 4.5, "yield": 5.2, "yield_unit": 6.0, "pop": 52_000, "auction_clearance": 52, "avg_dom": 42, "vacancy": 2.0, "walkability": 55, "council": "Greater Shepparton", "gentrification": "established", "infrastructure": "GV Health $229M Redevelopment + SAM Revitalisation"},
        {"name": "Wodonga", "postcode": "3690", "median": 460_000, "median_unit": 300_000, "growth": 4.2, "yield": 4.8, "yield_unit": 5.5, "pop": 33_000, "auction_clearance": 53, "avg_dom": 40, "vacancy": 1.8, "walkability": 55, "council": "Wodonga", "gentrification": "established", "infrastructure": "Wodonga Rail Bypass + Junction Place"},
        {"name": "Wangaratta", "postcode": "3677", "median": 430_000, "median_unit": 290_000, "growth": 4.0, "yield": 4.8, "yield_unit": 5.5, "pop": 19_000, "auction_clearance": 52, "avg_dom": 42, "vacancy": 1.8, "walkability": 58, "council": "Wangaratta", "gentrification": "established", "infrastructure": None},
        {"name": "Benalla", "postcode": "3672", "median": 370_000, "median_unit": 250_000, "growth": 4.5, "yield": 5.0, "yield_unit": 5.8, "pop": 10_000, "auction_clearance": 50, "avg_dom": 44, "vacancy": 2.2, "walkability": 52, "council": "Benalla", "gentrification": "established", "infrastructure": None},
        {"name": "Seymour", "postcode": "3660", "median": 380_000, "median_unit": 260_000, "growth": 4.8, "yield": 5.0, "yield_unit": 5.8, "pop": 7_000, "auction_clearance": 50, "avg_dom": 45, "vacancy": 2.2, "walkability": 50, "council": "Mitchell", "gentrification": "early", "infrastructure": "V/Line Service Frequency Upgrade"},
        {"name": "Mildura", "postcode": "3500", "median": 350_000, "median_unit": 240_000, "growth": 4.2, "yield": 5.5, "yield_unit": 6.5, "pop": 35_000, "auction_clearance": 48, "avg_dom": 48, "vacancy": 2.5, "walkability": 52, "council": "Mildura", "gentrification": "established", "infrastructure": "Mildura Airport Expansion + Murray River Trail"},
        {"name": "Swan Hill", "postcode": "3585", "median": 320_000, "median_unit": 220_000, "growth": 3.5, "yield": 5.8, "yield_unit": 6.8, "pop": 11_000, "auction_clearance": 46, "avg_dom": 50, "vacancy": 2.8, "walkability": 50, "council": "Swan Hill", "gentrification": "established", "infrastructure": None},
    ],
}


# ---------------------------------------------------------------------------
# Backward compatibility: API routes import AUSTRALIAN_REGIONS
# ---------------------------------------------------------------------------

# ═══════════════════════════════════════════════════════════════════
# NSW REGIONS: region → list of suburb dicts
# ═══════════════════════════════════════════════════════════════════

NSW_REGIONS: dict[str, list[dict]] = {

    "Sydney — CBD & Inner City": [
        {"name": "Sydney CBD", "postcode": "2000", "median": 1_350_000, "median_unit": 850_000, "growth": 2.5, "yield": 2.8, "yield_unit": 4.5, "pop": 35_000, "auction_clearance": 68, "avg_dom": 26, "vacancy": 2.8, "walkability": 98, "council": "City of Sydney", "gentrification": "mature", "infrastructure": "Sydney Metro West Station"},
        {"name": "Surry Hills", "postcode": "2010", "median": 1_750_000, "median_unit": 780_000, "growth": 2.0, "yield": 2.5, "yield_unit": 4.2, "pop": 16_000, "auction_clearance": 70, "avg_dom": 24, "vacancy": 2.0, "walkability": 96, "council": "City of Sydney", "gentrification": "premium", "infrastructure": None},
        {"name": "Chippendale", "postcode": "2008", "median": 1_500_000, "median_unit": 720_000, "growth": 2.8, "yield": 2.7, "yield_unit": 4.5, "pop": 8_500, "auction_clearance": 66, "avg_dom": 27, "vacancy": 2.2, "walkability": 94, "council": "City of Sydney", "gentrification": "mature", "infrastructure": "Central Station Metro upgrade"},
        {"name": "Ultimo", "postcode": "2007", "median": 1_400_000, "median_unit": 680_000, "growth": 2.2, "yield": 2.9, "yield_unit": 4.6, "pop": 10_000, "auction_clearance": 64, "avg_dom": 28, "vacancy": 2.5, "walkability": 93, "council": "City of Sydney", "gentrification": "mature", "infrastructure": None},
        {"name": "Pyrmont", "postcode": "2009", "median": 1_600_000, "median_unit": 900_000, "growth": 1.8, "yield": 2.6, "yield_unit": 4.0, "pop": 14_000, "auction_clearance": 65, "avg_dom": 30, "vacancy": 2.3, "walkability": 92, "council": "City of Sydney", "gentrification": "mature", "infrastructure": "Pyrmont Peninsula Renewal"},
        {"name": "Redfern", "postcode": "2016", "median": 1_650_000, "median_unit": 750_000, "growth": 3.0, "yield": 2.6, "yield_unit": 4.3, "pop": 13_500, "auction_clearance": 69, "avg_dom": 25, "vacancy": 1.8, "walkability": 94, "council": "City of Sydney", "gentrification": "established", "infrastructure": "Redfern Station Upgrade + Waterloo Metro"},
    ],

    "Sydney — Eastern Suburbs": [
        {"name": "Bondi", "postcode": "2026", "median": 3_200_000, "median_unit": 980_000, "growth": 1.5, "yield": 2.0, "yield_unit": 3.5, "pop": 11_000, "auction_clearance": 65, "avg_dom": 32, "vacancy": 1.8, "walkability": 82, "council": "Waverley", "gentrification": "premium", "infrastructure": None},
        {"name": "Coogee", "postcode": "2034", "median": 2_800_000, "median_unit": 850_000, "growth": 1.8, "yield": 2.1, "yield_unit": 3.6, "pop": 15_000, "auction_clearance": 66, "avg_dom": 30, "vacancy": 1.5, "walkability": 80, "council": "Randwick", "gentrification": "premium", "infrastructure": None},
        {"name": "Randwick", "postcode": "2031", "median": 2_500_000, "median_unit": 820_000, "growth": 2.2, "yield": 2.2, "yield_unit": 3.8, "pop": 30_000, "auction_clearance": 68, "avg_dom": 28, "vacancy": 1.6, "walkability": 78, "council": "Randwick", "gentrification": "mature", "infrastructure": "Sydney Light Rail (operational)"},
        {"name": "Maroubra", "postcode": "2035", "median": 2_200_000, "median_unit": 780_000, "growth": 2.8, "yield": 2.4, "yield_unit": 4.0, "pop": 32_000, "auction_clearance": 67, "avg_dom": 27, "vacancy": 1.4, "walkability": 72, "council": "Randwick", "gentrification": "established", "infrastructure": None},
    ],

    "Sydney — Inner West": [
        {"name": "Newtown", "postcode": "2042", "median": 1_800_000, "median_unit": 720_000, "growth": 2.5, "yield": 2.5, "yield_unit": 4.2, "pop": 15_000, "auction_clearance": 72, "avg_dom": 24, "vacancy": 1.5, "walkability": 92, "council": "Inner West", "gentrification": "mature", "infrastructure": None},
        {"name": "Marrickville", "postcode": "2204", "median": 1_600_000, "median_unit": 650_000, "growth": 3.0, "yield": 2.7, "yield_unit": 4.5, "pop": 26_000, "auction_clearance": 73, "avg_dom": 23, "vacancy": 1.4, "walkability": 85, "council": "Inner West", "gentrification": "established", "infrastructure": "Sydney Metro West Station (Marrickville)"},
        {"name": "Enmore", "postcode": "2042", "median": 1_700_000, "median_unit": 680_000, "growth": 2.8, "yield": 2.6, "yield_unit": 4.3, "pop": 6_000, "auction_clearance": 71, "avg_dom": 25, "vacancy": 1.5, "walkability": 90, "council": "Inner West", "gentrification": "established", "infrastructure": None},
        {"name": "Dulwich Hill", "postcode": "2203", "median": 1_550_000, "median_unit": 620_000, "growth": 3.2, "yield": 2.8, "yield_unit": 4.5, "pop": 13_000, "auction_clearance": 70, "avg_dom": 25, "vacancy": 1.3, "walkability": 80, "council": "Inner West", "gentrification": "established", "infrastructure": "Dulwich Hill Light Rail"},
        {"name": "Ashfield", "postcode": "2131", "median": 1_500_000, "median_unit": 600_000, "growth": 3.5, "yield": 2.9, "yield_unit": 4.6, "pop": 24_000, "auction_clearance": 69, "avg_dom": 26, "vacancy": 1.6, "walkability": 82, "council": "Inner West", "gentrification": "established", "infrastructure": "WestConnex (complete)"},
        {"name": "Petersham", "postcode": "2049", "median": 1_650_000, "median_unit": 640_000, "growth": 2.5, "yield": 2.6, "yield_unit": 4.4, "pop": 8_000, "auction_clearance": 70, "avg_dom": 26, "vacancy": 1.4, "walkability": 84, "council": "Inner West", "gentrification": "established", "infrastructure": None},
    ],

    "Sydney — North Shore": [
        {"name": "Mosman", "postcode": "2088", "median": 4_200_000, "median_unit": 1_100_000, "growth": 1.2, "yield": 1.8, "yield_unit": 3.2, "pop": 30_000, "auction_clearance": 62, "avg_dom": 35, "vacancy": 1.5, "walkability": 72, "council": "Mosman", "gentrification": "premium", "infrastructure": None},
        {"name": "Neutral Bay", "postcode": "2089", "median": 2_600_000, "median_unit": 850_000, "growth": 2.0, "yield": 2.2, "yield_unit": 3.8, "pop": 10_000, "auction_clearance": 66, "avg_dom": 28, "vacancy": 1.8, "walkability": 85, "council": "North Sydney", "gentrification": "premium", "infrastructure": None},
        {"name": "Chatswood", "postcode": "2067", "median": 2_200_000, "median_unit": 780_000, "growth": 2.5, "yield": 2.5, "yield_unit": 4.2, "pop": 25_000, "auction_clearance": 68, "avg_dom": 27, "vacancy": 1.6, "walkability": 80, "council": "Willoughby", "gentrification": "mature", "infrastructure": "Sydney Metro operational"},
        {"name": "Lane Cove", "postcode": "2066", "median": 2_100_000, "median_unit": 720_000, "growth": 2.8, "yield": 2.6, "yield_unit": 4.0, "pop": 12_000, "auction_clearance": 67, "avg_dom": 28, "vacancy": 1.4, "walkability": 70, "council": "Lane Cove", "gentrification": "mature", "infrastructure": None},
    ],

    "Sydney — Western Sydney": [
        {"name": "Parramatta", "postcode": "2150", "median": 1_100_000, "median_unit": 580_000, "growth": 3.5, "yield": 3.2, "yield_unit": 4.8, "pop": 32_000, "auction_clearance": 65, "avg_dom": 28, "vacancy": 1.8, "walkability": 78, "council": "City of Parramatta", "gentrification": "established", "infrastructure": "Sydney Metro West + Parramatta Light Rail"},
        {"name": "Blacktown", "postcode": "2148", "median": 850_000, "median_unit": 480_000, "growth": 4.5, "yield": 3.8, "yield_unit": 5.2, "pop": 48_000, "auction_clearance": 62, "avg_dom": 30, "vacancy": 1.5, "walkability": 60, "council": "Blacktown", "gentrification": "established", "infrastructure": None},
        {"name": "Penrith", "postcode": "2750", "median": 780_000, "median_unit": 440_000, "growth": 5.0, "yield": 4.0, "yield_unit": 5.4, "pop": 65_000, "auction_clearance": 60, "avg_dom": 32, "vacancy": 1.4, "walkability": 58, "council": "Penrith", "gentrification": "established", "infrastructure": "Western Sydney Airport (2026) + Metro"},
        {"name": "Liverpool", "postcode": "2170", "median": 800_000, "median_unit": 460_000, "growth": 4.8, "yield": 3.9, "yield_unit": 5.3, "pop": 30_000, "auction_clearance": 61, "avg_dom": 31, "vacancy": 1.5, "walkability": 62, "council": "Liverpool", "gentrification": "established", "infrastructure": "Liverpool Health & Academic Precinct"},
        {"name": "Campbelltown", "postcode": "2560", "median": 700_000, "median_unit": 420_000, "growth": 5.5, "yield": 4.2, "yield_unit": 5.5, "pop": 40_000, "auction_clearance": 58, "avg_dom": 34, "vacancy": 1.3, "walkability": 55, "council": "Campbelltown", "gentrification": "emerging", "infrastructure": "Western Sydney Airport jobs corridor"},
    ],

    "Sydney — South West Growth": [
        {"name": "Oran Park", "postcode": "2570", "median": 850_000, "median_unit": None, "growth": 5.2, "yield": 3.8, "yield_unit": None, "pop": 18_000, "auction_clearance": 57, "avg_dom": 35, "vacancy": 1.2, "walkability": 40, "council": "Camden", "gentrification": "early", "infrastructure": "Oran Park Town Centre + Metro"},
        {"name": "Leppington", "postcode": "2179", "median": 780_000, "median_unit": None, "growth": 5.8, "yield": 4.0, "yield_unit": None, "pop": 12_000, "auction_clearance": 56, "avg_dom": 37, "vacancy": 1.3, "walkability": 35, "council": "Liverpool/Camden", "gentrification": "early", "infrastructure": "Western Sydney Aerotropolis"},
        {"name": "Gregory Hills", "postcode": "2557", "median": 900_000, "median_unit": None, "growth": 4.5, "yield": 3.6, "yield_unit": None, "pop": 15_000, "auction_clearance": 58, "avg_dom": 34, "vacancy": 1.2, "walkability": 38, "council": "Camden", "gentrification": "established", "infrastructure": None},
    ],

    "Regional NSW — Hunter": [
        {"name": "Newcastle", "postcode": "2300", "median": 870_000, "median_unit": 580_000, "growth": 4.0, "yield": 4.0, "yield_unit": 5.2, "pop": 160_000, "auction_clearance": 60, "avg_dom": 30, "vacancy": 1.5, "walkability": 72, "council": "City of Newcastle", "gentrification": "established", "infrastructure": "Newcastle Light Rail + Hunter Street Revitalisation"},
        {"name": "Maitland", "postcode": "2320", "median": 650_000, "median_unit": 420_000, "growth": 4.5, "yield": 4.5, "yield_unit": 5.5, "pop": 85_000, "auction_clearance": 58, "avg_dom": 33, "vacancy": 1.2, "walkability": 55, "council": "Maitland", "gentrification": "established", "infrastructure": "Hunter Valley Rail Upgrade"},
        {"name": "Cessnock", "postcode": "2325", "median": 520_000, "median_unit": 350_000, "growth": 5.0, "yield": 5.2, "yield_unit": 6.0, "pop": 55_000, "auction_clearance": 55, "avg_dom": 36, "vacancy": 1.4, "walkability": 48, "council": "Cessnock", "gentrification": "emerging", "infrastructure": None},
    ],

    "Regional NSW — Central Coast & Illawarra": [
        {"name": "Gosford", "postcode": "2250", "median": 780_000, "median_unit": 520_000, "growth": 3.8, "yield": 3.8, "yield_unit": 5.0, "pop": 170_000, "auction_clearance": 58, "avg_dom": 32, "vacancy": 1.5, "walkability": 60, "council": "Central Coast", "gentrification": "established", "infrastructure": "Central Coast Health Hub"},
        {"name": "Wollongong", "postcode": "2500", "median": 850_000, "median_unit": 560_000, "growth": 3.5, "yield": 3.5, "yield_unit": 4.8, "pop": 210_000, "auction_clearance": 60, "avg_dom": 30, "vacancy": 1.3, "walkability": 68, "council": "Wollongong", "gentrification": "established", "infrastructure": "Wollongong Waterfront Renewal"},
        {"name": "Shellharbour", "postcode": "2529", "median": 780_000, "median_unit": 500_000, "growth": 4.0, "yield": 3.8, "yield_unit": 5.0, "pop": 75_000, "auction_clearance": 58, "avg_dom": 33, "vacancy": 1.4, "walkability": 52, "council": "Shellharbour", "gentrification": "established", "infrastructure": "Shell Cove Marina Development"},
    ],
}

# ═══════════════════════════════════════════════════════════════════
# QLD REGIONS
# ═══════════════════════════════════════════════════════════════════

QLD_REGIONS: dict[str, list[dict]] = {

    "Brisbane — Inner City": [
        {"name": "Brisbane CBD", "postcode": "4000", "median": 980_000, "median_unit": 520_000, "growth": 8.5, "yield": 3.5, "yield_unit": 5.5, "pop": 12_000, "auction_clearance": 55, "avg_dom": 18, "vacancy": 1.0, "walkability": 95, "council": "Brisbane City", "gentrification": "mature", "infrastructure": "Cross River Rail + Queen's Wharf"},
        {"name": "South Brisbane", "postcode": "4101", "median": 1_050_000, "median_unit": 580_000, "growth": 9.0, "yield": 3.3, "yield_unit": 5.2, "pop": 8_000, "auction_clearance": 56, "avg_dom": 17, "vacancy": 1.0, "walkability": 93, "council": "Brisbane City", "gentrification": "mature", "infrastructure": "South Bank Cultural Precinct Expansion"},
        {"name": "Fortitude Valley", "postcode": "4006", "median": 850_000, "median_unit": 480_000, "growth": 10.0, "yield": 3.8, "yield_unit": 5.8, "pop": 9_500, "auction_clearance": 54, "avg_dom": 19, "vacancy": 1.2, "walkability": 92, "council": "Brisbane City", "gentrification": "established", "infrastructure": "Cross River Rail Exhibition Station"},
        {"name": "New Farm", "postcode": "4005", "median": 1_800_000, "median_unit": 650_000, "growth": 7.5, "yield": 2.8, "yield_unit": 4.5, "pop": 12_500, "auction_clearance": 58, "avg_dom": 20, "vacancy": 0.8, "walkability": 88, "council": "Brisbane City", "gentrification": "premium", "infrastructure": None},
        {"name": "West End", "postcode": "4101", "median": 1_200_000, "median_unit": 540_000, "growth": 9.5, "yield": 3.2, "yield_unit": 5.3, "pop": 10_000, "auction_clearance": 55, "avg_dom": 18, "vacancy": 0.9, "walkability": 90, "council": "Brisbane City", "gentrification": "established", "infrastructure": "Kurilpa Riverfront Renewal"},
        {"name": "Woolloongabba", "postcode": "4102", "median": 950_000, "median_unit": 500_000, "growth": 12.0, "yield": 3.6, "yield_unit": 5.5, "pop": 8_500, "auction_clearance": 54, "avg_dom": 16, "vacancy": 0.8, "walkability": 85, "council": "Brisbane City", "gentrification": "emerging", "infrastructure": "2032 Olympics Gabba rebuild + Cross River Rail"},
    ],

    "Brisbane — North": [
        {"name": "Chermside", "postcode": "4032", "median": 780_000, "median_unit": 450_000, "growth": 10.5, "yield": 4.0, "yield_unit": 5.8, "pop": 12_000, "auction_clearance": 53, "avg_dom": 20, "vacancy": 0.8, "walkability": 72, "council": "Brisbane City", "gentrification": "established", "infrastructure": None},
        {"name": "Nundah", "postcode": "4012", "median": 850_000, "median_unit": 480_000, "growth": 9.5, "yield": 3.8, "yield_unit": 5.5, "pop": 13_000, "auction_clearance": 54, "avg_dom": 19, "vacancy": 0.9, "walkability": 75, "council": "Brisbane City", "gentrification": "established", "infrastructure": "Nundah Village Renewal"},
        {"name": "Aspley", "postcode": "4034", "median": 750_000, "median_unit": 430_000, "growth": 11.0, "yield": 4.2, "yield_unit": 5.8, "pop": 14_000, "auction_clearance": 52, "avg_dom": 21, "vacancy": 0.9, "walkability": 58, "council": "Brisbane City", "gentrification": "established", "infrastructure": None},
        {"name": "Everton Park", "postcode": "4053", "median": 780_000, "median_unit": None, "growth": 11.5, "yield": 4.0, "yield_unit": None, "pop": 8_000, "auction_clearance": 53, "avg_dom": 20, "vacancy": 0.8, "walkability": 55, "council": "Brisbane City", "gentrification": "emerging", "infrastructure": None},
    ],

    "Brisbane — South & Logan": [
        {"name": "Logan Central", "postcode": "4114", "median": 520_000, "median_unit": 340_000, "growth": 14.0, "yield": 5.5, "yield_unit": 6.8, "pop": 8_500, "auction_clearance": 48, "avg_dom": 22, "vacancy": 0.7, "walkability": 55, "council": "Logan", "gentrification": "early", "infrastructure": "Logan Metro Enhancement"},
        {"name": "Springwood", "postcode": "4127", "median": 620_000, "median_unit": 380_000, "growth": 12.5, "yield": 4.8, "yield_unit": 6.0, "pop": 11_000, "auction_clearance": 50, "avg_dom": 21, "vacancy": 0.8, "walkability": 55, "council": "Logan", "gentrification": "established", "infrastructure": None},
        {"name": "Beenleigh", "postcode": "4207", "median": 550_000, "median_unit": 350_000, "growth": 13.5, "yield": 5.2, "yield_unit": 6.5, "pop": 9_000, "auction_clearance": 49, "avg_dom": 23, "vacancy": 0.9, "walkability": 50, "council": "Logan", "gentrification": "early", "infrastructure": None},
        {"name": "Browns Plains", "postcode": "4118", "median": 580_000, "median_unit": 360_000, "growth": 13.0, "yield": 5.0, "yield_unit": 6.2, "pop": 12_000, "auction_clearance": 49, "avg_dom": 22, "vacancy": 0.8, "walkability": 48, "council": "Logan", "gentrification": "emerging", "infrastructure": None},
    ],

    "Gold Coast": [
        {"name": "Surfers Paradise", "postcode": "4217", "median": 1_050_000, "median_unit": 550_000, "growth": 10.0, "yield": 4.0, "yield_unit": 5.8, "pop": 23_000, "auction_clearance": 50, "avg_dom": 24, "vacancy": 1.0, "walkability": 82, "council": "Gold Coast", "gentrification": "mature", "infrastructure": "Gold Coast Light Rail Stage 3C"},
        {"name": "Broadbeach", "postcode": "4218", "median": 1_200_000, "median_unit": 600_000, "growth": 9.5, "yield": 3.8, "yield_unit": 5.5, "pop": 8_500, "auction_clearance": 52, "avg_dom": 22, "vacancy": 1.0, "walkability": 80, "council": "Gold Coast", "gentrification": "mature", "infrastructure": None},
        {"name": "Robina", "postcode": "4226", "median": 900_000, "median_unit": 500_000, "growth": 11.0, "yield": 4.2, "yield_unit": 5.5, "pop": 22_000, "auction_clearance": 51, "avg_dom": 23, "vacancy": 0.8, "walkability": 60, "council": "Gold Coast", "gentrification": "established", "infrastructure": "Robina Health Precinct Expansion"},
        {"name": "Coomera", "postcode": "4209", "median": 700_000, "median_unit": 420_000, "growth": 13.0, "yield": 4.8, "yield_unit": 5.8, "pop": 25_000, "auction_clearance": 48, "avg_dom": 25, "vacancy": 0.9, "walkability": 42, "council": "Gold Coast", "gentrification": "emerging", "infrastructure": "Coomera Town Centre + 2032 Olympics venue"},
        {"name": "Pimpama", "postcode": "4209", "median": 650_000, "median_unit": None, "growth": 14.0, "yield": 5.0, "yield_unit": None, "pop": 20_000, "auction_clearance": 47, "avg_dom": 26, "vacancy": 0.8, "walkability": 38, "council": "Gold Coast", "gentrification": "early", "infrastructure": None},
    ],

    "Sunshine Coast": [
        {"name": "Maroochydore", "postcode": "4558", "median": 900_000, "median_unit": 580_000, "growth": 8.5, "yield": 4.0, "yield_unit": 5.5, "pop": 18_000, "auction_clearance": 50, "avg_dom": 25, "vacancy": 0.8, "walkability": 65, "council": "Sunshine Coast", "gentrification": "established", "infrastructure": "Maroochydore CBD Development"},
        {"name": "Caloundra", "postcode": "4551", "median": 820_000, "median_unit": 520_000, "growth": 9.0, "yield": 4.2, "yield_unit": 5.5, "pop": 42_000, "auction_clearance": 49, "avg_dom": 26, "vacancy": 0.9, "walkability": 58, "council": "Sunshine Coast", "gentrification": "established", "infrastructure": "Direct Sunshine Coast Rail Line (proposed)"},
        {"name": "Nambour", "postcode": "4560", "median": 650_000, "median_unit": 400_000, "growth": 10.5, "yield": 4.8, "yield_unit": 6.0, "pop": 12_000, "auction_clearance": 47, "avg_dom": 28, "vacancy": 0.8, "walkability": 55, "council": "Sunshine Coast", "gentrification": "emerging", "infrastructure": "Nambour Activation Project"},
    ],

    "Regional QLD — Toowoomba & Ipswich": [
        {"name": "Toowoomba", "postcode": "4350", "median": 520_000, "median_unit": 340_000, "growth": 8.0, "yield": 5.0, "yield_unit": 6.2, "pop": 140_000, "auction_clearance": 46, "avg_dom": 28, "vacancy": 0.9, "walkability": 58, "council": "Toowoomba", "gentrification": "established", "infrastructure": "Inland Rail Hub + Second Range Crossing"},
        {"name": "Ipswich", "postcode": "4305", "median": 480_000, "median_unit": 320_000, "growth": 12.0, "yield": 5.5, "yield_unit": 6.8, "pop": 230_000, "auction_clearance": 48, "avg_dom": 24, "vacancy": 0.8, "walkability": 52, "council": "Ipswich", "gentrification": "emerging", "infrastructure": "Springfield Central expansion + Ipswich CBD Revitalisation"},
        {"name": "Springfield", "postcode": "4300", "median": 620_000, "median_unit": 380_000, "growth": 11.5, "yield": 4.8, "yield_unit": 5.8, "pop": 45_000, "auction_clearance": 50, "avg_dom": 23, "vacancy": 0.7, "walkability": 48, "council": "Ipswich", "gentrification": "established", "infrastructure": "Springfield Central Health City"},
    ],

    "Regional QLD — Cairns & Townsville": [
        {"name": "Cairns", "postcode": "4870", "median": 480_000, "median_unit": 280_000, "growth": 9.0, "yield": 5.5, "yield_unit": 7.0, "pop": 155_000, "auction_clearance": 42, "avg_dom": 30, "vacancy": 0.6, "walkability": 62, "council": "Cairns", "gentrification": "established", "infrastructure": "Cairns Shipping Development + Convention Centre Expansion"},
        {"name": "Townsville", "postcode": "4810", "median": 420_000, "median_unit": 260_000, "growth": 8.0, "yield": 5.8, "yield_unit": 7.2, "pop": 180_000, "auction_clearance": 40, "avg_dom": 32, "vacancy": 0.8, "walkability": 58, "council": "Townsville", "gentrification": "established", "infrastructure": "Townsville Stadium + CopperString 2.0"},
    ],
}

# ═══════════════════════════════════════════════════════════════════
# SA REGIONS
# ═══════════════════════════════════════════════════════════════════

SA_REGIONS: dict[str, list[dict]] = {

    "Adelaide — CBD & Inner": [
        {"name": "Adelaide CBD", "postcode": "5000", "median": 850_000, "median_unit": 450_000, "growth": 10.0, "yield": 3.8, "yield_unit": 5.5, "pop": 25_000, "auction_clearance": 72, "avg_dom": 16, "vacancy": 0.5, "walkability": 95, "council": "City of Adelaide", "gentrification": "mature", "infrastructure": "Lot Fourteen Innovation District"},
        {"name": "North Adelaide", "postcode": "5006", "median": 1_200_000, "median_unit": 520_000, "growth": 8.5, "yield": 3.2, "yield_unit": 4.8, "pop": 8_000, "auction_clearance": 70, "avg_dom": 18, "vacancy": 0.5, "walkability": 90, "council": "City of Adelaide", "gentrification": "premium", "infrastructure": None},
        {"name": "Norwood", "postcode": "5067", "median": 1_050_000, "median_unit": 480_000, "growth": 12.0, "yield": 3.5, "yield_unit": 5.0, "pop": 6_500, "auction_clearance": 73, "avg_dom": 15, "vacancy": 0.4, "walkability": 88, "council": "Norwood Payneham St Peters", "gentrification": "mature", "infrastructure": None},
        {"name": "Prospect", "postcode": "5082", "median": 920_000, "median_unit": 440_000, "growth": 13.0, "yield": 3.6, "yield_unit": 5.2, "pop": 22_000, "auction_clearance": 72, "avg_dom": 14, "vacancy": 0.4, "walkability": 82, "council": "City of Prospect", "gentrification": "established", "infrastructure": None},
        {"name": "Unley", "postcode": "5061", "median": 1_100_000, "median_unit": 490_000, "growth": 11.0, "yield": 3.3, "yield_unit": 4.8, "pop": 9_000, "auction_clearance": 74, "avg_dom": 16, "vacancy": 0.4, "walkability": 85, "council": "City of Unley", "gentrification": "mature", "infrastructure": None},
    ],

    "Adelaide — Northern": [
        {"name": "Elizabeth", "postcode": "5112", "median": 420_000, "median_unit": 250_000, "growth": 18.0, "yield": 5.8, "yield_unit": 7.5, "pop": 12_000, "auction_clearance": 68, "avg_dom": 12, "vacancy": 0.3, "walkability": 52, "council": "City of Playford", "gentrification": "early", "infrastructure": "Edinburgh Defence Precinct"},
        {"name": "Salisbury", "postcode": "5108", "median": 480_000, "median_unit": 280_000, "growth": 16.5, "yield": 5.5, "yield_unit": 7.0, "pop": 140_000, "auction_clearance": 69, "avg_dom": 13, "vacancy": 0.3, "walkability": 55, "council": "City of Salisbury", "gentrification": "emerging", "infrastructure": "Salisbury Centre Revitalisation"},
        {"name": "Gawler", "postcode": "5118", "median": 460_000, "median_unit": 280_000, "growth": 15.0, "yield": 5.2, "yield_unit": 6.8, "pop": 25_000, "auction_clearance": 66, "avg_dom": 15, "vacancy": 0.4, "walkability": 55, "council": "Town of Gawler", "gentrification": "emerging", "infrastructure": "Gawler East Growth Area"},
    ],

    "Adelaide — Southern": [
        {"name": "Morphett Vale", "postcode": "5162", "median": 550_000, "median_unit": 340_000, "growth": 15.5, "yield": 5.0, "yield_unit": 6.5, "pop": 30_000, "auction_clearance": 70, "avg_dom": 14, "vacancy": 0.3, "walkability": 48, "council": "City of Onkaparinga", "gentrification": "established", "infrastructure": None},
        {"name": "Christies Beach", "postcode": "5165", "median": 520_000, "median_unit": 320_000, "growth": 16.0, "yield": 5.2, "yield_unit": 6.8, "pop": 12_000, "auction_clearance": 69, "avg_dom": 13, "vacancy": 0.3, "walkability": 52, "council": "City of Onkaparinga", "gentrification": "emerging", "infrastructure": None},
        {"name": "Seaford", "postcode": "5169", "median": 530_000, "median_unit": 330_000, "growth": 15.0, "yield": 5.0, "yield_unit": 6.5, "pop": 10_000, "auction_clearance": 68, "avg_dom": 14, "vacancy": 0.4, "walkability": 45, "council": "City of Onkaparinga", "gentrification": "established", "infrastructure": "Seaford Rail Extension (complete)"},
        {"name": "Victor Harbor", "postcode": "5211", "median": 480_000, "median_unit": 310_000, "growth": 12.0, "yield": 4.5, "yield_unit": 5.8, "pop": 16_000, "auction_clearance": 62, "avg_dom": 20, "vacancy": 1.0, "walkability": 50, "council": "City of Victor Harbor", "gentrification": "established", "infrastructure": None},
    ],

    "Adelaide — Western & Port": [
        {"name": "Osborne", "postcode": "5017", "median": 520_000, "median_unit": 310_000, "growth": 18.0, "yield": 5.5, "yield_unit": 7.0, "pop": 3_500, "auction_clearance": 70, "avg_dom": 12, "vacancy": 0.3, "walkability": 40, "council": "City of Port Adelaide Enfield", "gentrification": "early", "infrastructure": "AUKUS Submarine Program — BAE Systems Osborne"},
        {"name": "Port Adelaide", "postcode": "5015", "median": 580_000, "median_unit": 340_000, "growth": 16.0, "yield": 5.0, "yield_unit": 6.5, "pop": 4_000, "auction_clearance": 69, "avg_dom": 14, "vacancy": 0.4, "walkability": 60, "council": "City of Port Adelaide Enfield", "gentrification": "emerging", "infrastructure": "Port Adelaide Renewal"},
        {"name": "Woodville", "postcode": "5011", "median": 620_000, "median_unit": 360_000, "growth": 15.0, "yield": 4.8, "yield_unit": 6.2, "pop": 5_000, "auction_clearance": 71, "avg_dom": 14, "vacancy": 0.4, "walkability": 65, "council": "City of Charles Sturt", "gentrification": "emerging", "infrastructure": None},
    ],
}

# ═══════════════════════════════════════════════════════════════════
# WA REGIONS
# ═══════════════════════════════════════════════════════════════════

WA_REGIONS: dict[str, list[dict]] = {

    "Perth — CBD & Inner": [
        {"name": "Perth CBD", "postcode": "6000", "median": 780_000, "median_unit": 420_000, "growth": 15.0, "yield": 4.2, "yield_unit": 5.8, "pop": 10_000, "auction_clearance": 46, "avg_dom": 12, "vacancy": 0.5, "walkability": 94, "council": "City of Perth", "gentrification": "mature", "infrastructure": "Perth City Link + Elizabeth Quay"},
        {"name": "Subiaco", "postcode": "6008", "median": 1_200_000, "median_unit": 520_000, "growth": 12.0, "yield": 3.5, "yield_unit": 5.0, "pop": 17_000, "auction_clearance": 48, "avg_dom": 14, "vacancy": 0.5, "walkability": 85, "council": "City of Subiaco", "gentrification": "premium", "infrastructure": "Subiaco-Subi East Redevelopment"},
        {"name": "Leederville", "postcode": "6007", "median": 1_000_000, "median_unit": 480_000, "growth": 14.0, "yield": 3.8, "yield_unit": 5.5, "pop": 6_500, "auction_clearance": 47, "avg_dom": 12, "vacancy": 0.4, "walkability": 88, "council": "City of Vincent", "gentrification": "established", "infrastructure": None},
        {"name": "Mt Lawley", "postcode": "6050", "median": 1_050_000, "median_unit": 460_000, "growth": 13.5, "yield": 3.6, "yield_unit": 5.2, "pop": 8_000, "auction_clearance": 47, "avg_dom": 13, "vacancy": 0.4, "walkability": 82, "council": "City of Stirling", "gentrification": "mature", "infrastructure": None},
        {"name": "Northbridge", "postcode": "6003", "median": 700_000, "median_unit": 380_000, "growth": 16.0, "yield": 4.5, "yield_unit": 6.0, "pop": 4_000, "auction_clearance": 45, "avg_dom": 11, "vacancy": 0.5, "walkability": 92, "council": "City of Perth", "gentrification": "emerging", "infrastructure": "Perth City Link Stage 2"},
    ],

    "Perth — Northern Corridor": [
        {"name": "Joondalup", "postcode": "6027", "median": 650_000, "median_unit": 380_000, "growth": 18.0, "yield": 4.5, "yield_unit": 6.0, "pop": 32_000, "auction_clearance": 44, "avg_dom": 12, "vacancy": 0.4, "walkability": 62, "council": "City of Joondalup", "gentrification": "established", "infrastructure": "METRONET Joondalup Line Extension"},
        {"name": "Wanneroo", "postcode": "6065", "median": 550_000, "median_unit": 340_000, "growth": 20.0, "yield": 5.0, "yield_unit": 6.5, "pop": 15_000, "auction_clearance": 43, "avg_dom": 11, "vacancy": 0.3, "walkability": 45, "council": "City of Wanneroo", "gentrification": "emerging", "infrastructure": "METRONET Yanchep Rail Extension"},
        {"name": "Two Rocks", "postcode": "6037", "median": 450_000, "median_unit": None, "growth": 22.0, "yield": 5.5, "yield_unit": None, "pop": 5_000, "auction_clearance": 42, "avg_dom": 10, "vacancy": 0.3, "walkability": 30, "council": "City of Wanneroo", "gentrification": "early", "infrastructure": "Yanchep Rail Line (2025)"},
    ],

    "Perth — Southern Corridor": [
        {"name": "Fremantle", "postcode": "6160", "median": 850_000, "median_unit": 480_000, "growth": 15.0, "yield": 3.8, "yield_unit": 5.5, "pop": 8_500, "auction_clearance": 46, "avg_dom": 14, "vacancy": 0.5, "walkability": 80, "council": "City of Fremantle", "gentrification": "established", "infrastructure": "Fremantle Port Inner Harbour Renewal"},
        {"name": "Rockingham", "postcode": "6168", "median": 520_000, "median_unit": 340_000, "growth": 19.0, "yield": 5.0, "yield_unit": 6.5, "pop": 40_000, "auction_clearance": 43, "avg_dom": 11, "vacancy": 0.3, "walkability": 55, "council": "City of Rockingham", "gentrification": "established", "infrastructure": "METRONET Rockingham Line"},
        {"name": "Mandurah", "postcode": "6210", "median": 480_000, "median_unit": 320_000, "growth": 18.5, "yield": 5.2, "yield_unit": 6.8, "pop": 85_000, "auction_clearance": 42, "avg_dom": 12, "vacancy": 0.4, "walkability": 52, "council": "City of Mandurah", "gentrification": "established", "infrastructure": None},
        {"name": "Armadale", "postcode": "6112", "median": 420_000, "median_unit": 280_000, "growth": 22.0, "yield": 5.8, "yield_unit": 7.0, "pop": 80_000, "auction_clearance": 41, "avg_dom": 10, "vacancy": 0.3, "walkability": 48, "council": "City of Armadale", "gentrification": "early", "infrastructure": "METRONET Byford Extension"},
    ],

    "Regional WA": [
        {"name": "Bunbury", "postcode": "6230", "median": 460_000, "median_unit": 300_000, "growth": 16.0, "yield": 5.5, "yield_unit": 7.0, "pop": 75_000, "auction_clearance": 38, "avg_dom": 15, "vacancy": 0.5, "walkability": 58, "council": "City of Bunbury", "gentrification": "established", "infrastructure": "Bunbury Outer Ring Road + Port Expansion"},
        {"name": "Geraldton", "postcode": "6530", "median": 340_000, "median_unit": 210_000, "growth": 14.0, "yield": 6.5, "yield_unit": 8.0, "pop": 40_000, "auction_clearance": 35, "avg_dom": 18, "vacancy": 0.6, "walkability": 50, "council": "City of Greater Geraldton", "gentrification": "established", "infrastructure": None},
        {"name": "Karratha", "postcode": "6714", "median": 480_000, "median_unit": 280_000, "growth": 15.0, "yield": 6.0, "yield_unit": 7.5, "pop": 22_000, "auction_clearance": 32, "avg_dom": 20, "vacancy": 0.8, "walkability": 42, "council": "City of Karratha", "gentrification": "established", "infrastructure": "Perdaman Urea Plant + NWS LNG expansion"},
    ],
}

# ═══════════════════════════════════════════════════════════════════
# TAS REGIONS
# ═══════════════════════════════════════════════════════════════════

TAS_REGIONS: dict[str, list[dict]] = {

    "Hobart & Southern TAS": [
        {"name": "Hobart CBD", "postcode": "7000", "median": 680_000, "median_unit": 450_000, "growth": -1.0, "yield": 4.0, "yield_unit": 5.0, "pop": 55_000, "auction_clearance": 50, "avg_dom": 32, "vacancy": 1.2, "walkability": 82, "council": "City of Hobart", "gentrification": "mature", "infrastructure": "Hobart City Deal — Macquarie Point Renewal"},
        {"name": "Sandy Bay", "postcode": "7005", "median": 950_000, "median_unit": 550_000, "growth": -0.5, "yield": 3.5, "yield_unit": 4.5, "pop": 12_000, "auction_clearance": 52, "avg_dom": 30, "vacancy": 1.0, "walkability": 78, "council": "City of Hobart", "gentrification": "premium", "infrastructure": None},
        {"name": "Glenorchy", "postcode": "7010", "median": 520_000, "median_unit": 360_000, "growth": -2.0, "yield": 4.8, "yield_unit": 5.8, "pop": 46_000, "auction_clearance": 48, "avg_dom": 35, "vacancy": 1.3, "walkability": 60, "council": "City of Glenorchy", "gentrification": "established", "infrastructure": "Northern Suburbs Transit Corridor"},
        {"name": "Kingston", "postcode": "7050", "median": 620_000, "median_unit": 400_000, "growth": -1.5, "yield": 4.2, "yield_unit": 5.2, "pop": 18_000, "auction_clearance": 49, "avg_dom": 34, "vacancy": 1.2, "walkability": 52, "council": "Kingborough", "gentrification": "established", "infrastructure": None},
    ],

    "Launceston & Northern TAS": [
        {"name": "Launceston", "postcode": "7250", "median": 480_000, "median_unit": 320_000, "growth": 0.0, "yield": 5.0, "yield_unit": 6.0, "pop": 70_000, "auction_clearance": 46, "avg_dom": 38, "vacancy": 1.3, "walkability": 65, "council": "City of Launceston", "gentrification": "established", "infrastructure": "UTAS Inveresk Campus + City Heart Project"},
        {"name": "Devonport", "postcode": "7310", "median": 400_000, "median_unit": 280_000, "growth": 1.0, "yield": 5.5, "yield_unit": 6.5, "pop": 26_000, "auction_clearance": 44, "avg_dom": 40, "vacancy": 1.5, "walkability": 55, "council": "Devonport City", "gentrification": "established", "infrastructure": "Devonport Living City Transformation"},
        {"name": "Burnie", "postcode": "7320", "median": 380_000, "median_unit": 260_000, "growth": 0.5, "yield": 5.8, "yield_unit": 6.8, "pop": 20_000, "auction_clearance": 42, "avg_dom": 42, "vacancy": 1.6, "walkability": 55, "council": "Burnie City", "gentrification": "established", "infrastructure": None},
    ],
}

# ═══════════════════════════════════════════════════════════════════
# NT REGIONS
# ═══════════════════════════════════════════════════════════════════

NT_REGIONS: dict[str, list[dict]] = {

    "Darwin & Surrounds": [
        {"name": "Darwin CBD", "postcode": "0800", "median": 580_000, "median_unit": 310_000, "growth": 2.5, "yield": 5.5, "yield_unit": 6.5, "pop": 12_000, "auction_clearance": 36, "avg_dom": 52, "vacancy": 2.5, "walkability": 80, "council": "City of Darwin", "gentrification": "mature", "infrastructure": "Darwin City Deal — Darwin Waterfront Stage 2"},
        {"name": "Stuart Park", "postcode": "0820", "median": 650_000, "median_unit": 340_000, "growth": 2.0, "yield": 5.2, "yield_unit": 6.2, "pop": 4_000, "auction_clearance": 35, "avg_dom": 50, "vacancy": 2.2, "walkability": 72, "council": "City of Darwin", "gentrification": "established", "infrastructure": None},
        {"name": "Palmerston", "postcode": "0830", "median": 450_000, "median_unit": 280_000, "growth": 3.0, "yield": 6.0, "yield_unit": 7.0, "pop": 38_000, "auction_clearance": 34, "avg_dom": 48, "vacancy": 2.0, "walkability": 50, "council": "City of Palmerston", "gentrification": "established", "infrastructure": "Palmerston Regional Hospital"},
        {"name": "Casuarina", "postcode": "0810", "median": 500_000, "median_unit": 290_000, "growth": 2.5, "yield": 5.8, "yield_unit": 6.8, "pop": 5_500, "auction_clearance": 35, "avg_dom": 50, "vacancy": 2.3, "walkability": 55, "council": "City of Darwin", "gentrification": "established", "infrastructure": None},
    ],

    "Alice Springs": [
        {"name": "Alice Springs", "postcode": "0870", "median": 420_000, "median_unit": 250_000, "growth": 1.5, "yield": 6.5, "yield_unit": 7.5, "pop": 27_000, "auction_clearance": 30, "avg_dom": 60, "vacancy": 3.0, "walkability": 55, "council": "Town of Alice Springs", "gentrification": "established", "infrastructure": "National Aboriginal Art Gallery"},
    ],
}

# ═══════════════════════════════════════════════════════════════════
# ACT REGIONS
# ═══════════════════════════════════════════════════════════════════

ACT_REGIONS: dict[str, list[dict]] = {

    "Canberra — Inner North & South": [
        {"name": "Canberra CBD (Civic)", "postcode": "2601", "median": 1_050_000, "median_unit": 550_000, "growth": 1.5, "yield": 3.2, "yield_unit": 5.0, "pop": 6_000, "auction_clearance": 56, "avg_dom": 28, "vacancy": 1.8, "walkability": 90, "council": "ACT Government", "gentrification": "mature", "infrastructure": "City Renewal Authority — City Plan"},
        {"name": "Braddon", "postcode": "2612", "median": 980_000, "median_unit": 520_000, "growth": 2.0, "yield": 3.5, "yield_unit": 5.2, "pop": 5_000, "auction_clearance": 57, "avg_dom": 26, "vacancy": 1.5, "walkability": 88, "council": "ACT Government", "gentrification": "mature", "infrastructure": "Light Rail Stage 1 (operational)"},
        {"name": "Kingston", "postcode": "2604", "median": 1_100_000, "median_unit": 580_000, "growth": 1.8, "yield": 3.0, "yield_unit": 4.8, "pop": 8_000, "auction_clearance": 55, "avg_dom": 29, "vacancy": 1.6, "walkability": 82, "council": "ACT Government", "gentrification": "mature", "infrastructure": "Kingston Arts Precinct"},
        {"name": "Barton", "postcode": "2600", "median": 1_200_000, "median_unit": 600_000, "growth": 1.0, "yield": 2.8, "yield_unit": 4.5, "pop": 3_000, "auction_clearance": 54, "avg_dom": 30, "vacancy": 2.0, "walkability": 78, "council": "ACT Government", "gentrification": "premium", "infrastructure": None},
    ],

    "Canberra — Belconnen & Gungahlin": [
        {"name": "Belconnen", "postcode": "2617", "median": 800_000, "median_unit": 450_000, "growth": 2.0, "yield": 4.0, "yield_unit": 5.5, "pop": 100_000, "auction_clearance": 54, "avg_dom": 28, "vacancy": 1.8, "walkability": 62, "council": "ACT Government", "gentrification": "established", "infrastructure": "Belconnen Town Centre Renewal"},
        {"name": "Gungahlin", "postcode": "2912", "median": 820_000, "median_unit": 460_000, "growth": 2.5, "yield": 3.8, "yield_unit": 5.3, "pop": 80_000, "auction_clearance": 55, "avg_dom": 27, "vacancy": 1.5, "walkability": 55, "council": "ACT Government", "gentrification": "established", "infrastructure": "Light Rail Stage 2A to Woden"},
        {"name": "Casey", "postcode": "2913", "median": 780_000, "median_unit": None, "growth": 2.8, "yield": 4.0, "yield_unit": None, "pop": 18_000, "auction_clearance": 54, "avg_dom": 28, "vacancy": 1.3, "walkability": 42, "council": "ACT Government", "gentrification": "established", "infrastructure": None},
    ],

    "Canberra — Woden & Tuggeranong": [
        {"name": "Woden", "postcode": "2606", "median": 880_000, "median_unit": 480_000, "growth": 1.5, "yield": 3.5, "yield_unit": 5.0, "pop": 35_000, "auction_clearance": 53, "avg_dom": 30, "vacancy": 1.8, "walkability": 65, "council": "ACT Government", "gentrification": "established", "infrastructure": "CIT Woden Campus + Light Rail Stage 2A"},
        {"name": "Tuggeranong", "postcode": "2900", "median": 720_000, "median_unit": 420_000, "growth": 1.0, "yield": 4.2, "yield_unit": 5.5, "pop": 90_000, "auction_clearance": 52, "avg_dom": 32, "vacancy": 2.0, "walkability": 50, "council": "ACT Government", "gentrification": "established", "infrastructure": None},
    ],

    "Canberra — Molonglo & Weston Creek": [
        {"name": "Molonglo Valley", "postcode": "2611", "median": 850_000, "median_unit": None, "growth": 3.0, "yield": 3.5, "yield_unit": None, "pop": 20_000, "auction_clearance": 56, "avg_dom": 26, "vacancy": 1.0, "walkability": 35, "council": "ACT Government", "gentrification": "early", "infrastructure": "Molonglo Stage 3 Urban Release — 30,000+ residents planned"},
        {"name": "Weston", "postcode": "2611", "median": 900_000, "median_unit": 460_000, "growth": 1.5, "yield": 3.5, "yield_unit": 5.0, "pop": 5_000, "auction_clearance": 53, "avg_dom": 30, "vacancy": 1.5, "walkability": 55, "council": "ACT Government", "gentrification": "mature", "infrastructure": None},
    ],
}


AUSTRALIAN_REGIONS: dict[str, dict[str, list[dict]]] = {
    "NSW": NSW_REGIONS,
    "VIC": VIC_REGIONS,
    "QLD": QLD_REGIONS,
    "SA": SA_REGIONS,
    "WA": WA_REGIONS,
    "TAS": TAS_REGIONS,
    "NT": NT_REGIONS,
    "ACT": ACT_REGIONS,
}


# ---------------------------------------------------------------------------
# Utility functions — same API signatures for backward compat
# ---------------------------------------------------------------------------

def get_all_states() -> list[str]:
    """Return all states with location data."""
    return list(AUSTRALIAN_REGIONS.keys())


def get_regions_for_state(state: str) -> list[str]:
    """Return region names for a given state."""
    return list(AUSTRALIAN_REGIONS.get(state.upper(), {}).keys())


def get_suburbs_for_region(state: str, region: str) -> list[dict]:
    """Return suburb data for a given state and region."""
    return AUSTRALIAN_REGIONS.get(state.upper(), {}).get(region, [])


def get_all_suburbs_for_state(state: str) -> list[dict]:
    """Return all suburbs across all regions in a state."""
    suburbs = []
    for region_name, region_suburbs in AUSTRALIAN_REGIONS.get(state.upper(), {}).items():
        for sub in region_suburbs:
            suburbs.append({**sub, "region": region_name})
    return suburbs


def get_all_suburbs() -> list[dict]:
    """Return every suburb across all states."""
    all_subs = []
    for state, regions in AUSTRALIAN_REGIONS.items():
        for region_name, region_suburbs in regions.items():
            for sub in region_suburbs:
                all_subs.append({**sub, "state": state, "region": region_name})
    return all_subs


def get_location_tree() -> dict:
    """Return a hierarchical tree: state → region → suburbs (names only)."""
    tree = {}
    for state, regions in AUSTRALIAN_REGIONS.items():
        tree[state] = {}
        for region_name, suburbs in regions.items():
            tree[state][region_name] = [s["name"] for s in suburbs]
    return tree


def get_location_summary() -> dict:
    """Return summary stats for the location database."""
    total_states = len(AUSTRALIAN_REGIONS)
    total_regions = sum(len(regions) for regions in AUSTRALIAN_REGIONS.values())
    total_suburbs = sum(
        len(suburbs)
        for regions in AUSTRALIAN_REGIONS.values()
        for suburbs in regions.values()
    )
    # Compute aggregate VIC stats
    all_subs = get_all_suburbs()
    avg_median = sum(s["median"] for s in all_subs) / len(all_subs) if all_subs else 0
    avg_yield = sum(s["yield"] for s in all_subs) / len(all_subs) if all_subs else 0
    avg_growth = sum(s["growth"] for s in all_subs) / len(all_subs) if all_subs else 0
    avg_auction = sum(s.get("auction_clearance", 60) for s in all_subs) / len(all_subs) if all_subs else 0
    avg_vacancy = sum(s.get("vacancy", 2.0) for s in all_subs) / len(all_subs) if all_subs else 0

    return {
        "total_states": total_states,
        "total_regions": total_regions,
        "total_suburbs": total_suburbs,
        "market_snapshot": {
            "avg_median_house": round(avg_median),
            "avg_gross_yield": round(avg_yield, 1),
            "avg_growth_12m": round(avg_growth, 1),
            "avg_auction_clearance": round(avg_auction, 1),
            "avg_vacancy_rate": round(avg_vacancy, 1),
        },
    }


def _fuzzy_score(query: str, target: str) -> float:
    """Simple fuzzy similarity score (0-1) using character n-gram overlap."""
    if not query or not target:
        return 0.0
    q = query.lower()
    t = target.lower()
    # Exact substring → perfect
    if q in t:
        return 1.0
    # Bigram overlap for typo tolerance
    def bigrams(s: str) -> set[str]:
        return {s[i:i+2] for i in range(len(s) - 1)} if len(s) >= 2 else {s}
    q_bg = bigrams(q)
    t_bg = bigrams(t)
    if not q_bg or not t_bg:
        return 0.0
    overlap = len(q_bg & t_bg)
    return overlap / max(len(q_bg), len(t_bg))


def search_suburbs(query: str, fuzzy: bool = True) -> list[dict]:
    """Search for suburbs matching a query string (name or postcode).

    With *fuzzy=True* (default), also returns approximate matches for
    misspellings, scored and sorted by relevance.
    """
    query_lower = query.lower().strip()
    exact: list[tuple[float, dict]] = []
    fuzzy_hits: list[tuple[float, dict]] = []

    for state, regions in AUSTRALIAN_REGIONS.items():
        for region_name, suburbs in regions.items():
            for sub in suburbs:
                name_lower = sub["name"].lower()
                postcode = sub.get("postcode", "")
                enriched = {**sub, "state": state, "region": region_name}

                # Exact / substring match → top priority
                if query_lower in name_lower or query_lower in postcode:
                    exact.append((1.0, enriched))
                elif fuzzy:
                    score = _fuzzy_score(query_lower, name_lower)
                    if score >= 0.35:  # reasonable threshold
                        fuzzy_hits.append((score, enriched))

    # Sort: exact first (preserve order), then fuzzy by score desc
    fuzzy_hits.sort(key=lambda x: x[0], reverse=True)
    combined = [item for _, item in exact] + [item for _, item in fuzzy_hits]
    return combined


def get_suburb_detail(suburb_name: str) -> dict | None:
    """Get full details for a specific suburb including enriched market data."""
    for state, regions in AUSTRALIAN_REGIONS.items():
        for region_name, suburbs in regions.items():
            for sub in suburbs:
                if sub["name"].lower() == suburb_name.lower():
                    return {**sub, "state": state, "region": region_name}
    return None


def get_gentrification_hotspots() -> list[dict]:
    """Return suburbs in 'early' or 'emerging' gentrification stages — highest upside."""
    hotspots = []
    for state, regions in AUSTRALIAN_REGIONS.items():
        for region_name, suburbs in regions.items():
            for sub in suburbs:
                if sub.get("gentrification") in ("early", "emerging"):
                    hotspots.append({**sub, "state": state, "region": region_name})
    hotspots.sort(key=lambda x: x.get("growth", 0), reverse=True)
    return hotspots


def get_infrastructure_suburbs() -> list[dict]:
    """Return suburbs with active infrastructure pipeline projects."""
    infra = []
    for state, regions in AUSTRALIAN_REGIONS.items():
        for region_name, suburbs in regions.items():
            for sub in suburbs:
                if sub.get("infrastructure"):
                    infra.append({**sub, "state": state, "region": region_name})
    return infra


def compute_suburb_investment_score(suburb: dict) -> dict:
    """
    Compute a composite investment attractiveness score for a suburb.

    Returns score (0-100) and breakdown across dimensions.
    """
    # Yield score (0-25): higher yield = better
    yld = suburb.get("yield", 3.0)
    yield_score = min(25, yld * 5)

    # Growth score (0-25): higher growth = better
    growth = suburb.get("growth", 2.0)
    growth_score = min(25, growth * 5)

    # Affordability score (0-20): lower median = more accessible
    median = suburb.get("median", 800_000)
    if median <= 500_000:
        afford_score = 20
    elif median <= 800_000:
        afford_score = 15
    elif median <= 1_200_000:
        afford_score = 10
    elif median <= 1_800_000:
        afford_score = 5
    else:
        afford_score = 2

    # Vacancy score (0-15): lower vacancy = stronger demand
    vacancy = suburb.get("vacancy", 2.0)
    vacancy_score = max(0, 15 - vacancy * 5)

    # Infrastructure bonus (0-15)
    infra_bonus = 10 if suburb.get("infrastructure") else 0
    if suburb.get("gentrification") in ("early", "emerging"):
        infra_bonus += 5

    total = round(yield_score + growth_score + afford_score + vacancy_score + infra_bonus)

    return {
        "total_score": min(100, total),
        "yield_score": round(yield_score, 1),
        "growth_score": round(growth_score, 1),
        "affordability_score": round(afford_score, 1),
        "demand_score": round(vacancy_score, 1),
        "infrastructure_score": round(infra_bonus, 1),
    }
