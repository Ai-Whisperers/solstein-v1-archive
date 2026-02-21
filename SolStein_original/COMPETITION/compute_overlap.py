"""
Compute the 33x33 competitive overlap matrix for FD-016.

Scoring: 4 dimensions, each 0 or 1. Score = min(3, sum of dimensions).
Tier encoding: T1=1, T1b=2, T2=3, T3=4. Adjacent = |diff| <= 1.
"""
import json

competitors = [
    # (short, full, geo, products, customers, tier_encoded)
    # Tier encoding: T1=1, T1b=2, T2=3, T3=4. Adjacent means |t1-t2| <= 1
    ("Eneve", "Eneve (formerly Energy21)",
     {"NL","BE","UK"}, {"BO","BI"}, {"RET","TRD","IND"}, 1),
    ("SOPTIM", "SOPTIM AG",
     {"DE","AT"}, {"BO"}, {"RET","GRD"}, 1),
    ("Trayport", "Trayport (TMX Group)",
     {"UK","NL"}, {"ET"}, {"TRD","RET"}, 1),
    ("Brady", "Brady Technologies",
     {"UK","NO","PL","US"}, {"ET","BO"}, {"RET","TRD"}, 1),
    ("Volue", "Volue ASA",
     {"NO","DE","IT","AT","PL"}, {"BO","ET","FC"}, {"RET","TRD","GRD"}, 1),
    ("KISTERS", "KISTERS AG",
     {"DE","AT","NL"}, {"BO"}, {"RET","GRD"}, 1),
    ("SopraS", "Sopra Steria (cpX.Energy)",
     {"FR","DE","NL","BE","UK"}, {"BO","PL"}, {"RET"}, 1),
    ("Engrate", "Engrate AB",
     {"NO","DE","NL"}, {"BO","PL"}, {"RET","TRD","GRD"}, 1),
    ("Hansen", "Hansen Technologies",
     {"NL","UK","DE","NO"}, {"BI"}, {"RET"}, 1),
    ("Robotron", "Robotron Datenbank-Software GmbH",
     {"DE"}, {"BI"}, {"RET"}, 2),
    ("EG", "EG A/S (Utility Division)",
     {"NO"}, {"BI"}, {"RET"}, 2),
    ("Tietoevry", "Tietoevry (Tieto)",
     {"NO"}, {"BI","CO"}, {"RET"}, 2),
    ("MaxBill", "MaxBill (LogNet Systems)",
     {"UK","NL","PL"}, {"BI"}, {"RET"}, 2),
    ("Indra", "Indra Sistemas / Minsait",
     {"ES","IT"}, {"BO","PL"}, {"RET","GRD"}, 2),
    ("EngGrp", "Engineering Group",
     {"IT","ES","DE","BE"}, {"BI"}, {"RET"}, 2),
    ("Ferranti", "Ferranti Computer Systems",
     {"BE","UK","IT","CH","DE"}, {"BI"}, {"RET"}, 2),
    ("Asseco", "Asseco Poland S.A.",
     {"PL","EE"}, {"BI"}, {"RET"}, 2),
    ("ION", "ION Commodities (ION Group)",
     {"UK","US"}, {"ET"}, {"TRD"}, 3),
    ("Hitachi", "Hitachi Energy",
     {"CH","US","DE"}, {"ET"}, {"RET","TRD","GRD"}, 3),
    ("EnergyOne", "Energy One Limited",
     {"UK","FR","BE"}, {"ET"}, {"RET","TRD"}, 3),
    ("Previse", "Previse Systems AG",
     {"CH","DE","NL","UK","NO","ES","IT","PL","BE"}, {"ET"}, {"TRD","RET"}, 3),
    ("Orchestr", "Orchestrade Financial Systems",
     {"FR","UK","BE","PL"}, {"ET"}, {"TRD"}, 3),
    ("Molecule", "Molecule Software",
     {"US","UK"}, {"ET"}, {"TRD"}, 3),
    ("Qualia", "Qualia Trading",
     {"UK"}, {"ET"}, {"TRD"}, 3),
    ("Octopus", "Octopus Energy / Kraken Technologies",
     {"UK","FR","IT","DE","ES"}, {"PL","BI"}, {"RET"}, 4),
    ("tem", "tem (tem energy)",
     {"UK"}, {"PL"}, {"IND"}, 4),
    ("Dexter", "Dexter Energy",
     {"NL","DE","BE","FR","UK","IT"}, {"FC","BO"}, {"GEN","TRD","RET"}, 4),
    ("ALTEN", "ALTEN Worldgrid",
     {"FR","ES","DE"}, {"CO"}, {"RET","GRD"}, 4),
    ("CGI", "CGI Inc.",
     {"NL","FR","UK"}, {"PL","IN"}, {"GRD","INF"}, 4),
    ("SEEBURGER", "SEEBURGER AG",
     {"DE"}, {"IN"}, {"INF"}, 4),
    ("Arvato", "Arvato Systems (Bertelsmann)",
     {"DE","NL"}, {"IN","BI"}, {"RET","GRD"}, 4),
    ("Schleupen", "Schleupen SE",
     {"DE"}, {"BI","IN"}, {"RET"}, 4),
    ("Creatica", "Creatica GmbH",
     {"DE"}, {"ET"}, {"TRD","GEN"}, 4),
]

N = len(competitors)

def overlap_score(a, b):
    geo = 1 if len(a[2] & b[2]) > 0 else 0
    prod = 1 if len(a[3] & b[3]) > 0 else 0
    cust = 1 if len(a[4] & b[4]) > 0 else 0
    tier = 1 if abs(a[5] - b[5]) <= 1 else 0
    return min(3, geo + prod + cust + tier)

def raw_dims(a, b):
    geo = 1 if len(a[2] & b[2]) > 0 else 0
    prod = 1 if len(a[3] & b[3]) > 0 else 0
    cust = 1 if len(a[4] & b[4]) > 0 else 0
    tier = 1 if abs(a[5] - b[5]) <= 1 else 0
    return geo, prod, cust, tier

matrix = [[0]*N for _ in range(N)]
for i in range(N):
    for j in range(N):
        if i == j:
            matrix[i][j] = -1
        else:
            matrix[i][j] = overlap_score(competitors[i], competitors[j])

from collections import Counter
score_counts = Counter()
for i in range(N):
    for j in range(i+1, N):
        score_counts[matrix[i][j]] += 1

lines = []
lines.append("=== SCORE DISTRIBUTION ===")
for score in sorted(score_counts.keys()):
    pct = score_counts[score] / 528 * 100
    lines.append(f"  Score {score}: {score_counts[score]} pairs ({pct:.0f}%)")

# Eneve row with detail
lines.append("\n=== ENEVE OVERLAP DETAIL ===")
env = competitors[0]
for j in range(1, N):
    c = competitors[j]
    g, p, cu, t = raw_dims(env, c)
    lines.append(f"  {c[0]:12s}: score={matrix[0][j]}  [geo={g} prod={p} cust={cu} tier={t}]")

# Most connected
score3_count = {}
for i in range(N):
    name = competitors[i][0]
    cnt = sum(1 for j in range(N) if j != i and matrix[i][j] == 3)
    score3_count[name] = cnt

lines.append("\n=== MOST OVERLAPPING COMPANIES (score-3 count) ===")
for name, cnt in sorted(score3_count.items(), key=lambda x: -x[1])[:10]:
    lines.append(f"  {name:12s}: {cnt} direct overlaps")

# Top 5 overlap pairs (raw=4, then by product+geo depth)
raw_pairs = []
for i in range(N):
    for j in range(i+1, N):
        g, p, cu, t = raw_dims(competitors[i], competitors[j])
        raw = g + p + cu + t
        geo_cnt = len(competitors[i][2] & competitors[j][2])
        prod_cnt = len(competitors[i][3] & competitors[j][3])
        cust_cnt = len(competitors[i][4] & competitors[j][4])
        raw_pairs.append((raw, geo_cnt + prod_cnt + cust_cnt, competitors[i][0], competitors[j][0]))

raw_pairs.sort(reverse=True)
lines.append("\n=== TOP 5 MOST OVERLAPPING PAIRS ===")
for raw, depth, a, b in raw_pairs[:5]:
    lines.append(f"  {a} <-> {b}: dimensions={raw}/4, overlap_depth={depth}")

# Full matrix as numbers (for building markdown later)
lines.append("\n=== FULL MATRIX (numeric) ===")
shorts = [c[0] for c in competitors]
header = f"{'':13s}" + "".join(f"{s[:6]:>7s}" for s in shorts)
lines.append(header)
for i in range(N):
    row = f"{shorts[i][:12]:13s}"
    for j in range(N):
        if i == j:
            row += "    ---"
        else:
            row += f"      {matrix[i][j]}"
        
    lines.append(row)

# Write to file
output = "\n".join(lines)
with open("overlap_results.txt", "w", encoding="utf-8") as f:
    f.write(output)

# Also write the matrix as JSON for easy processing
matrix_data = {
    "competitors": [c[0] for c in competitors],
    "full_names": [c[1] for c in competitors],
    "matrix": matrix,
    "top_5_pairs": [(a, b, raw, depth) for raw, depth, a, b in raw_pairs[:5]],
}
with open("overlap_matrix.json", "w", encoding="utf-8") as f:
    json.dump(matrix_data, f, indent=2)

print("Done. Output written to overlap_results.txt and overlap_matrix.json")
print(f"\nScore distribution: {dict(sorted(score_counts.items()))}")
print(f"Eneve score-3 overlaps: {score3_count.get('Eneve', 0)}")
