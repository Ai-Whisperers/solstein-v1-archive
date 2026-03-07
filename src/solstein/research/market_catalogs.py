"""Market catalogs for company discovery.

EPIC-020: Extracted from _catalog_for_market function.
Market catalogs are now data-driven instead of hardcoded in functions.
"""

from __future__ import annotations

# Dutch/Energy market catalog
DUTCH_ENERGY_CATALOG = [
    {
        "name": "Eneve",
        "ticker": None,
        "industry": "Energy Software",
        "region": "NL",
        "tags": ["energy", "software", "billing"],
        "sources": [
            "https://eneve.com/",
            "https://www.linkedin.com/company/eneve/",
        ],
    },
    {
        "name": "Octopus Energy Group / Kraken Technologies",
        "ticker": None,
        "industry": "Energy Software",
        "region": "UK/EU",
        "tags": ["energy", "platform", "kraken"],
        "sources": ["https://octopus.energy/", "https://kraken.tech/"],
    },
    {
        "name": "Volue ASA",
        "ticker": "VOLUE.OL",
        "industry": "Energy Software",
        "region": "Nordics/EU",
        "tags": ["energy", "trading", "optimization"],
        "sources": [
            "https://www.volue.com/",
            "https://finance.yahoo.com/quote/VOLUE.OL/",
        ],
    },
    {
        "name": "CGI Inc.",
        "ticker": "GIB",
        "industry": "IT Services",
        "region": "Global/EU",
        "tags": ["consulting", "utilities", "software"],
        "sources": [
            "https://www.cgi.com/",
            "https://finance.yahoo.com/quote/GIB/",
        ],
    },
    {
        "name": "Accenture",
        "ticker": "ACN",
        "industry": "IT Services",
        "region": "Global/EU",
        "tags": ["consulting", "utilities", "cloud"],
        "sources": [
            "https://www.accenture.com/",
            "https://finance.yahoo.com/quote/ACN/",
        ],
    },
    {
        "name": "Capgemini",
        "ticker": "CAP.PA",
        "industry": "IT Services",
        "region": "EU",
        "tags": ["consulting", "energy", "transformation"],
        "sources": [
            "https://www.capgemini.com/",
            "https://finance.yahoo.com/quote/CAP.PA/",
        ],
    },
    {
        "name": "TCS (Tata Consultancy Services)",
        "ticker": "TCS.NS",
        "industry": "IT Services",
        "region": "Global",
        "tags": ["consulting", "utilities", "digital"],
        "sources": [
            "https://www.tcs.com/",
            "https://finance.yahoo.com/quote/TCS.NS/",
        ],
    },
    {
        "name": "Infosys",
        "ticker": "INFY",
        "industry": "IT Services",
        "region": "Global",
        "tags": ["consulting", "energy", "automation"],
        "sources": [
            "https://www.infosys.com/",
            "https://finance.yahoo.com/quote/INFY/",
        ],
    },
    {
        "name": "Sopra Steria",
        "ticker": "SOP.PA",
        "industry": "IT Services",
        "region": "EU",
        "tags": ["consulting", "energy", "digital"],
        "sources": [
            "https://www.soprasteria.com/",
            "https://finance.yahoo.com/quote/SOP.PA/",
        ],
    },
    {
        "name": "Eneco",
        "ticker": None,
        "industry": "Energy Utility",
        "region": "NL",
        "tags": ["energy", "utility", "sustainability"],
        "sources": [
            "https://www.eneco.com/",
            "https://www.linkedin.com/company/eneco/",
        ],
    },
    {
        "name": "Vattenfall",
        "ticker": None,
        "industry": "Energy Utility",
        "region": "Nordics/EU",
        "tags": ["energy", "utility", "renewables"],
        "sources": [
            "https://group.vattenfall.com/",
            "https://www.linkedin.com/company/vattenfall/",
        ],
    },
    {
        "name": "TenneT",
        "ticker": None,
        "industry": "Grid Operator",
        "region": "NL/DE",
        "tags": ["grid", "transmission", "infrastructure"],
        "sources": [
            "https://www.tennet.eu/",
            "https://www.linkedin.com/company/tennet/",
        ],
    },
    {
        "name": "Stedin",
        "ticker": None,
        "industry": "Grid Operator",
        "region": "NL",
        "tags": ["grid", "distribution", "infrastructure"],
        "sources": [
            "https://www.stedin.net/",
            "https://www.linkedin.com/company/stedin/",
        ],
    },
    {
        "name": "Alliander",
        "ticker": None,
        "industry": "Grid Operator",
        "region": "NL",
        "tags": ["grid", "distribution", "innovation"],
        "sources": [
            "https://www.alliander.com/",
            "https://www.linkedin.com/company/alliander/",
        ],
    },
    {
        "name": "Shell",
        "ticker": "SHEL",
        "industry": "Integrated Energy",
        "region": "Global",
        "tags": ["oil", "gas", "energy transition"],
        "sources": [
            "https://www.shell.com/",
            "https://finance.yahoo.com/quote/SHEL/",
        ],
    },
    {
        "name": "BP",
        "ticker": "BP",
        "industry": "Integrated Energy",
        "region": "Global",
        "tags": ["oil", "gas", "renewables"],
        "sources": [
            "https://www.bp.com/",
            "https://finance.yahoo.com/quote/BP/",
        ],
    },
    {
        "name": "TotalEnergies",
        "ticker": "TTE",
        "industry": "Integrated Energy",
        "region": "Global/EU",
        "tags": ["oil", "gas", "renewables"],
        "sources": [
            "https://totalenergies.com/",
            "https://finance.yahoo.com/quote/TTE/",
        ],
    },
    {
        "name": "Equinor",
        "ticker": "EQNR",
        "industry": "Integrated Energy",
        "region": "Nordics/EU",
        "tags": ["oil", "gas", "offshore wind"],
        "sources": [
            "https://www.equinor.com/",
            "https://finance.yahoo.com/quote/EQNR/",
        ],
    },
    {
        "name": "Orsted",
        "ticker": "ORSTED.CO",
        "industry": "Renewables Developer",
        "region": "DK/Global",
        "tags": ["offshore wind", "renewables", "green energy"],
        "sources": [
            "https://orsted.com/",
            "https://finance.yahoo.com/quote/ORSTED.CO/",
        ],
    },
    {
        "name": "Siemens Energy",
        "ticker": "ENR.DE",
        "industry": "Energy Technology",
        "region": "Global/EU",
        "tags": ["turbines", "grid", "technology"],
        "sources": [
            "https://www.siemens-energy.com/",
            "https://finance.yahoo.com/quote/ENR.DE/",
        ],
    },
    {
        "name": "GE Vernova",
        "ticker": "GEV",
        "industry": "Energy Technology",
        "region": "Global",
        "tags": ["turbines", "grid", "technology"],
        "sources": [
            "https://www.gevernova.com/",
            "https://finance.yahoo.com/quote/GEV/",
        ],
    },
    {
        "name": "Schneider Electric",
        "ticker": "SU.PA",
        "industry": "Energy Management",
        "region": "Global/EU",
        "tags": ["automation", "digital", "efficiency"],
        "sources": [
            "https://www.se.com/",
            "https://finance.yahoo.com/quote/SU.PA/",
        ],
    },
    {
        "name": "ABB",
        "ticker": "ABBNY",
        "industry": "Electrification",
        "region": "Global/EU",
        "tags": ["automation", "electrification", "digital"],
        "sources": [
            "https://global.abb/",
            "https://finance.yahoo.com/quote/ABBNY/",
        ],
    },
    {
        "name": "Hitachi Energy",
        "ticker": None,
        "industry": "Grid Technology",
        "region": "Global",
        "tags": ["grid", "power quality", "digital"],
        "sources": [
            "https://www.hitachienergy.com/",
            "https://www.linkedin.com/company/hitachi-energy/",
        ],
    },
]

# LATAM Fintech market catalog
LATAM_FINTECH_CATALOG = [
    {
        "name": "Nu Holdings (Nubank)",
        "ticker": "NU",
        "industry": "Digital Banking",
        "region": "LATAM",
        "tags": ["neobank", "credit", "digital"],
        "sources": [
            "https://international.nubank.com.br/",
            "https://finance.yahoo.com/quote/NU/",
        ],
    },
    {
        "name": "Banco Inter",
        "ticker": "INTR",
        "industry": "Digital Banking",
        "region": "LATAM",
        "tags": ["neobank", "super-app", "digital"],
        "sources": [
            "https://www.bancointer.com.br/",
            "https://finance.yahoo.com/quote/INTR/",
        ],
    },
    {
        "name": "StoneCo",
        "ticker": "STNE",
        "industry": "Payments",
        "region": "LATAM",
        "tags": ["payments", "fintech", "SMB"],
        "sources": [
            "https://investors.stone.co/",
            "https://finance.yahoo.com/quote/STNE/",
        ],
    },
    {
        "name": "PagSeguro",
        "ticker": "PAGS",
        "industry": "Payments",
        "region": "LATAM",
        "tags": ["payments", "fintech", "digital"],
        "sources": [
            "https://investors.pagseguro.com/",
            "https://finance.yahoo.com/quote/PAGS/",
        ],
    },
    {
        "name": "dLocal",
        "ticker": "DLO",
        "industry": "Cross-border Payments",
        "region": "LATAM",
        "tags": ["payments", "cross-border", "emerging markets"],
        "sources": [
            "https://www.dlocal.com/",
            "https://finance.yahoo.com/quote/DLO/",
        ],
    },
    {
        "name": "MercadoLibre",
        "ticker": "MELI",
        "industry": "E-commerce / Fintech",
        "region": "LATAM",
        "tags": ["marketplace", "payments", "fintech"],
        "sources": [
            "https://investor.mercadolibre.com/",
            "https://finance.yahoo.com/quote/MELI/",
        ],
    },
    {
        "name": "Creditas",
        "ticker": None,
        "industry": "Lending",
        "region": "LATAM",
        "tags": ["lending", "secured loans", "fintech"],
        "sources": [
            "https://www.creditas.com/",
            "https://www.linkedin.com/company/creditas/",
        ],
    },
    {
        "name": "EBANX",
        "ticker": None,
        "industry": "Payments",
        "region": "LATAM",
        "tags": ["payments", "cross-border", "ecommerce"],
        "sources": [
            "https://business.ebanx.com/",
            "https://www.linkedin.com/company/ebanx/",
        ],
    },
    {
        "name": "Kavak",
        "ticker": None,
        "industry": "Auto Fintech",
        "region": "LATAM",
        "tags": ["auto", "marketplace", "fintech"],
        "sources": [
            "https://www.kavak.com/",
            "https://www.linkedin.com/company/kavak/",
        ],
    },
    {
        "name": "Ualá",
        "ticker": None,
        "industry": "Digital Banking",
        "region": "LATAM",
        "tags": ["neobank", "financial inclusion", "digital"],
        "sources": [
            "https://www.uala.com.ar/",
            "https://www.linkedin.com/company/uala/",
        ],
    },
    {
        "name": "C6 Bank",
        "ticker": None,
        "industry": "Digital Banking",
        "region": "LATAM",
        "tags": ["neobank", "digital", "banking"],
        "sources": [
            "https://www.c6bank.com.br/",
            "https://www.linkedin.com/company/c6bank/",
        ],
    },
    {
        "name": "Neon",
        "ticker": None,
        "industry": "Digital Banking",
        "region": "LATAM",
        "tags": ["neobank", "financial inclusion", "digital"],
        "sources": [
            "https://neon.com.br/",
            "https://www.linkedin.com/company/neonpagamentos/",
        ],
    },
    {
        "name": "Intercorp Financial Services",
        "ticker": "IFS",
        "industry": "Banking",
        "region": "LATAM",
        "tags": ["bank", "retail", "financial"],
        "sources": [
            "https://www.ifhperu.com/",
            "https://finance.yahoo.com/quote/IFS/",
        ],
    },
    {
        "name": "XP Inc.",
        "ticker": "XP",
        "industry": "Wealth & Brokerage",
        "region": "LATAM",
        "tags": ["brokerage", "investment", "fintech"],
        "sources": [
            "https://investors.xpinc.com/",
            "https://finance.yahoo.com/quote/XP/",
        ],
    },
    {
        "name": "MercadoLibre Fintech",
        "ticker": "MELI",
        "industry": "Payments",
        "region": "LATAM",
        "tags": ["payments", "wallet", "fintech"],
        "sources": [
            "https://investor.mercadolibre.com/",
            "https://finance.yahoo.com/quote/MELI/",
        ],
    },
    {
        "name": "Banorte",
        "ticker": "GFNORTEO.MX",
        "industry": "Banking",
        "region": "LATAM",
        "tags": ["bank", "retail", "enterprise"],
        "sources": [
            "https://www.banorte.com/",
            "https://finance.yahoo.com/quote/GFNORTEO.MX/",
        ],
    },
    {
        "name": "BBAJIO",
        "ticker": "BBAJIOO.MX",
        "industry": "Banking",
        "region": "LATAM",
        "tags": ["bank", "commercial", "financial"],
        "sources": [
            "https://www.bb.com.mx/",
            "https://finance.yahoo.com/quote/BBAJIOO.MX/",
        ],
    },
    {
        "name": "Gentera",
        "ticker": "GENTERA.MX",
        "industry": "Financial Services",
        "region": "LATAM",
        "tags": ["microfinance", "lending", "financial"],
        "sources": [
            "https://gentera.com.mx/",
            "https://finance.yahoo.com/quote/GENTERA.MX/",
        ],
    },
]

# Market to catalog mapping
MARKET_CATALOGS = {
    "dutch": DUTCH_ENERGY_CATALOG,
    "netherlands": DUTCH_ENERGY_CATALOG,
    "energy": DUTCH_ENERGY_CATALOG,
    "latam": LATAM_FINTECH_CATALOG,
    "fintech": LATAM_FINTECH_CATALOG,
}


def get_catalog_for_market(market: str) -> list[dict[str, object]]:
    """Get company catalog for a given market.

    EPIC-020: Refactored from 429-line _catalog_for_market function.
    Now uses data-driven approach with MARKET_CATALOGS mapping.
    """
    market_lower = market.lower()

    # Check for exact match first
    if market_lower in MARKET_CATALOGS:
        return MARKET_CATALOGS[market_lower]

    # Check for partial match
    for key, catalog in MARKET_CATALOGS.items():
        if key in market_lower:
            return catalog

    # Return empty catalog for unknown markets
    return []
