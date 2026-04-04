# STORY-278: Add stock tickers for all publicly traded catalog companies

| Field | Value |
|-------|-------|
| **Epic** | EPIC-071 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Add stock ticker symbols to all publicly traded companies in the Dutch Energy market catalog. Verify each ticker on Yahoo Finance before adding.

Known tickers: Volue=VOLUE.OL, Shell=SHEL, BP=BP.L, Equinor=EQNR, Orsted=ORSTED.CO, Siemens Energy=ENR.DE, GE Vernova=GEV, Schneider=SU.PA, ABB=ABBN.SW, Hitachi=6501.T, Accenture=ACN, CGI=GIB, TCS=TCS.NS, Infosys=INFY, Sopra=SOP.PA, Capgemini=CAP.PA

## Acceptance Criteria

- [ ] All publicly traded catalog companies have a verified stock ticker
- [ ] Tickers verified on Yahoo Finance (produce valid quote)
- [ ] Private companies have `ticker = None`

## Technical Notes

- File: `src/solstein/data/market_catalogs.py`
- Pure data entry — no logic changes
