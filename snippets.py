# =============================================================================
# FAERS DATA CLEANING SCRIPT
# Copy each CELL block into a separate Jupyter notebook cell in order.
# =============================================================================


# ── CELL 1: Imports ───────────────────────────────────────────────────────────

import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

print("Imports loaded successfully")


# ── CELL 2: Paths ────────────────────────────────────────────────────────────

QUARTERS = {
    'Q1': '/Users/mymacbook/Desktop/Booth Spring 2026/Data Visualization/Final Project/FAERS Data/Untouched/faers_ascii_2025q1/ASCII',
    'Q2': '/Users/mymacbook/Desktop/Booth Spring 2026/Data Visualization/Final Project/FAERS Data/Untouched/faers_ascii_2025q2/ASCII',
    'Q3': '/Users/mymacbook/Desktop/Booth Spring 2026/Data Visualization/Final Project/FAERS Data/Untouched/faers_ascii_2025q3/ASCII',
    'Q4': '/Users/mymacbook/Desktop/Booth Spring 2026/Data Visualization/Final Project/FAERS Data/Untouched/faers_ascii_2025Q4 (1)/ASCII',
}

OUT_DIR = '/Users/mymacbook/Desktop/Booth Spring 2026/Data Visualization/Final Project/FAERS Data/output_clean'
os.makedirs(OUT_DIR, exist_ok=True)

print("Paths configured")
for q, path in QUARTERS.items():
    print(f"  {q}: {'OK' if os.path.exists(path) else 'NOT FOUND'}")


# ── CELL 3: Load all quarters ─────────────────────────────────────────────────

FILE_TYPES = ['DEMO', 'DRUG', 'REAC', 'OUTC', 'INDI', 'RPSR', 'THER']
QUARTER_SUFFIX = {'Q1': '25Q1', 'Q2': '25Q2', 'Q3': '25Q3', 'Q4': '25Q4'}

raw = {}

for ftype in FILE_TYPES:
    frames = []
    for q, path in QUARTERS.items():
        filename = f"{ftype}{QUARTER_SUFFIX[q]}.txt"
        filepath = os.path.join(path, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, sep='$', encoding='latin1', low_memory=False)
            df['quarter'] = q
            frames.append(df)
            print(f"  Loaded {filename}: {len(df):,} rows")
        else:
            print(f"  SKIPPED (not found): {filename}")
    raw[ftype] = pd.concat(frames, ignore_index=True)
    print(f"  --> {ftype} total: {len(raw[ftype]):,} rows\n")

print("All files loaded!")


# ── CELL 4: Deduplicate ───────────────────────────────────────────────────────

demo_raw = raw['DEMO'].copy()
demo_raw['primaryid'] = pd.to_numeric(demo_raw['primaryid'], errors='coerce')
demo_raw = demo_raw.sort_values('primaryid', ascending=False)
demo_dedup = demo_raw.drop_duplicates(subset='caseid', keep='first')

print(f"DEMO before dedup: {len(demo_raw):,}")
print(f"DEMO after dedup:  {len(demo_dedup):,}")
print(f"Duplicate cases removed: {len(demo_raw) - len(demo_dedup):,}")

valid_ids = set(demo_dedup['primaryid'])
print(f"\nValid primaryids: {len(valid_ids):,}")

for ftype in ['DRUG', 'REAC', 'OUTC', 'INDI', 'RPSR', 'THER']:
    before = len(raw[ftype])
    raw[ftype]['primaryid'] = pd.to_numeric(raw[ftype]['primaryid'], errors='coerce')
    raw[ftype] = raw[ftype][raw[ftype]['primaryid'].isin(valid_ids)]
    print(f"  {ftype}: {before:,} → {len(raw[ftype]):,} rows")


# ── CELL 5: Clean DEMO ───────────────────────────────────────────────────────

sex_map = {'M': 'Male', 'F': 'Female', 'UNK': 'Unknown'}
age_grp_map = {
    'N': 'Neonate', 'I': 'Infant', 'C': 'Child',
    'T': 'Adolescent', 'A': 'Adult', 'E': 'Elderly'
}
occp_map = {
    'MD': 'Physician', 'PH': 'Pharmacist', 'OT': 'Other HCP',
    'LW': 'Lawyer', 'CN': 'Consumer', 'HP': 'Health Professional'
}

demo = demo_dedup.copy()
demo['sex_label']     = demo['sex'].map(sex_map).fillna('Unknown')
demo['age_grp_label'] = demo['age_grp'].map(age_grp_map).fillna('Unknown')
demo['reporter_type'] = demo['occp_cod'].map(occp_map).fillna('Unknown')

demo_clean = demo[[
    'primaryid', 'caseid', 'sex_label', 'age_grp_label',
    'reporter_type', 'reporter_country', 'fda_dt', 'quarter'
]].copy()

print(f"demo_clean: {len(demo_clean):,} rows")
print("\nSex breakdown:")
print(demo_clean['sex_label'].value_counts())
print("\nAge group breakdown:")
print(demo_clean['age_grp_label'].value_counts())
print("\nReporter type breakdown:")
print(demo_clean['reporter_type'].value_counts())


# ── CELL 6: Clean OUTC (worst outcome per case) ───────────────────────────────

outcome_map = {
    'DE': 'Death',
    'LT': 'Life-Threatening',
    'HO': 'Hospitalization',
    'DS': 'Disability',
    'CA': 'Congenital Anomaly',
    'RI': 'Required Intervention',
    'OT': 'Other Serious'
}
severity_rank = {
    'Death': 1, 'Life-Threatening': 2, 'Hospitalization': 3,
    'Disability': 4, 'Required Intervention': 5,
    'Congenital Anomaly': 6, 'Other Serious': 7
}

outc = raw['OUTC'].copy()
outc['outcome_label'] = outc['outc_cod'].map(outcome_map).fillna('Unknown')
outc['severity_rank'] = outc['outcome_label'].map(severity_rank).fillna(99)
worst_outc = (
    outc.sort_values('severity_rank')
    .groupby('primaryid', as_index=False)
    .first()[['primaryid', 'outcome_label']]
    .rename(columns={'outcome_label': 'worst_outcome'})
)

print(f"worst_outc: {len(worst_outc):,} rows")
print("\nWorst outcome distribution:")
print(worst_outc['worst_outcome'].value_counts())


# ── CELL 7: Clean DRUG (primary suspect only + GLP-1 flag) ───────────────────

GLP1_BRANDS   = ['OZEMPIC', 'WEGOVY', 'MOUNJARO', 'ZEPBOUND', 'RYBELSUS',
                  'VICTOZA', 'TRULICITY', 'SAXENDA']
GLP1_GENERICS = ['SEMAGLUTIDE', 'TIRZEPATIDE', 'LIRAGLUTIDE',
                  'DULAGLUTIDE', 'EXENATIDE']
GLP1_ALL = set(GLP1_BRANDS + GLP1_GENERICS)

drug = raw['DRUG'].copy()
drug['drugname'] = drug['drugname'].str.upper().str.strip()

# Primary suspect only
ps_drug = drug[drug['role_cod'] == 'PS'].copy()
ps_drug['is_glp1'] = ps_drug['drugname'].isin(GLP1_ALL)

print(f"All drug rows:            {len(drug):,}")
print(f"Primary suspect rows:     {len(ps_drug):,}")
print(f"GLP-1 primary suspect:    {ps_drug['is_glp1'].sum():,}")
print("\nGLP-1 drug breakdown:")
print(ps_drug[ps_drug['is_glp1']]['drugname'].value_counts())


# ── CELL 8: Clean REAC ───────────────────────────────────────────────────────

DOSING_ERROR_TERMS = [
    'Incorrect dose administered',
    'Extra dose administered',
    'Accidental underdose',
    'Product dose omission issue',
    'Overdose',
    'Underdose'
]

reac = raw['REAC'].copy()
reac['pt'] = reac['pt'].str.strip()
reac['is_dosing_error'] = reac['pt'].isin(DOSING_ERROR_TERMS)
reac['is_offlabel'] = reac['pt'] == 'Off label use'

print(f"reac rows: {len(reac):,}")
print(f"Dosing error reactions: {reac['is_dosing_error'].sum():,}")
print(f"Off-label reactions:    {reac['is_offlabel'].sum():,}")
print("\nTop 15 reactions:")
print(reac['pt'].value_counts().head(15))


# ── CELL 9: Clean INDI ───────────────────────────────────────────────────────

indi = raw['INDI'].copy()
indi['indi_pt'] = indi['indi_pt'].str.strip()

print(f"indi rows: {len(indi):,}")
print("\nTop 15 indications:")
print(indi['indi_pt'].value_counts().head(15))


# ── CELL 10: Clean RPSR ──────────────────────────────────────────────────────

rpsr_map = {
    'FGN': 'Foreign',
    'SDN': 'Study',
    'LIT': 'Literature',
    'CSM': 'Consumer/Spontaneous',
    'HP':  'Health Professional',
    'UF':  'User Facility',
    'OTC': 'Over the Counter',
    'MFR': 'Manufacturer',
    'DT':  'Distributor'
}

rpsr = raw['RPSR'].copy()
rpsr['report_source'] = rpsr['rpsr_cod'].map(rpsr_map).fillna('Other')

print(f"rpsr rows: {len(rpsr):,}")
print("\nReport source breakdown:")
print(rpsr['report_source'].value_counts())


# ── CELL 11: THER — therapy duration ─────────────────────────────────────────

ther = raw['THER'].copy()
ther['start_dt'] = pd.to_datetime(ther['start_dt'], format='%Y%m%d', errors='coerce')
ther['end_dt']   = pd.to_datetime(ther['end_dt'],   format='%Y%m%d', errors='coerce')
ther['duration_days'] = (ther['end_dt'] - ther['start_dt']).dt.days

valid_dur = ther['duration_days'].notna() & (ther['duration_days'] >= 0)
print(f"THER rows:               {len(ther):,}")
print(f"Rows with valid duration: {valid_dur.sum():,} ({valid_dur.mean()*100:.1f}%)")
print(f"\nDuration stats (days):")
print(ther.loc[valid_dur, 'duration_days'].describe())


# ── CELL 12: Build master table ───────────────────────────────────────────────

master = (
    demo_clean
    .merge(worst_outc, on='primaryid', how='left')
)
master['worst_outcome'] = master['worst_outcome'].fillna('No Outcome Reported')

print(f"Master table: {len(master):,} rows")
print("\nOutcome distribution:")
print(master['worst_outcome'].value_counts())


# ── CELL 13: OUTPUT — Demographics (Dashboard 1 + 2) ─────────────────────────

master.to_csv(f'{OUT_DIR}/faers_demographics.csv', index=False)
print(f"Saved faers_demographics.csv ({len(master):,} rows)")


# ── CELL 14: OUTPUT — Drug summary (Dashboard 1 + 2 scatter) ─────────────────

drug_outc = ps_drug[['primaryid', 'drugname']].merge(worst_outc, on='primaryid', how='left')
drug_outc['worst_outcome'] = drug_outc['worst_outcome'].fillna('No Outcome Reported')

drug_summary = (
    drug_outc
    .groupby(['drugname', 'worst_outcome'])
    .size()
    .reset_index(name='report_count')
)

drug_pivot = drug_summary.pivot_table(
    index='drugname', columns='worst_outcome',
    values='report_count', fill_value=0
).reset_index()
drug_pivot.columns.name = None
drug_pivot['total_reports'] = drug_pivot.drop('drugname', axis=1).sum(axis=1)
drug_pivot['death_count']   = drug_pivot.get('Death', 0)
drug_pivot['death_rate_pct'] = (drug_pivot['death_count'] / drug_pivot['total_reports'] * 100).round(2)
drug_pivot = drug_pivot.sort_values('total_reports', ascending=False)

# Top 300 for Tableau
drug_pivot.head(300).to_csv(f'{OUT_DIR}/faers_drug_summary.csv', index=False)
print(f"Saved faers_drug_summary.csv (top 300 drugs)")
print(drug_pivot.head(10)[['drugname', 'total_reports', 'death_count', 'death_rate_pct']])


# ── CELL 15: OUTPUT — Drug long format (Dashboard 1) ─────────────────────────

outcome_cols = [c for c in drug_pivot.columns if c not in
                ['drugname', 'total_reports', 'death_count', 'death_rate_pct']]

drug_long = drug_pivot.head(300).melt(
    id_vars=['drugname', 'total_reports', 'death_rate_pct'],
    value_vars=outcome_cols,
    var_name='outcome',
    value_name='report_count'
)
drug_long = drug_long[drug_long['report_count'] > 0]
drug_long.to_csv(f'{OUT_DIR}/faers_drug_long.csv', index=False)
print(f"Saved faers_drug_long.csv ({len(drug_long):,} rows)")


# ── CELL 16: OUTPUT — Reaction summary (Dashboard 1) ─────────────────────────

reac_outc = reac[['primaryid', 'pt']].merge(worst_outc, on='primaryid', how='left')
reac_outc['worst_outcome'] = reac_outc['worst_outcome'].fillna('No Outcome Reported')

reac_pivot = (
    reac_outc
    .groupby(['pt', 'worst_outcome'])
    .size()
    .reset_index(name='count')
    .pivot_table(index='pt', columns='worst_outcome', values='count', fill_value=0)
    .reset_index()
)
reac_pivot.columns.name = None
reac_pivot['total'] = reac_pivot.drop('pt', axis=1).sum(axis=1)
reac_pivot = reac_pivot.sort_values('total', ascending=False)
reac_pivot.head(150).to_csv(f'{OUT_DIR}/faers_reaction_summary.csv', index=False)
print(f"Saved faers_reaction_summary.csv (top 150 reactions)")
print(reac_pivot.head(10)[['pt', 'total']])


# ── CELL 17: OUTPUT — KPIs (Dashboard 1) ─────────────────────────────────────

kpis = pd.DataFrame([{
    'total_reports':      len(master),
    'total_deaths':       (master['worst_outcome'] == 'Death').sum(),
    'total_hospitalized': (master['worst_outcome'] == 'Hospitalization').sum(),
    'unique_drugs':       ps_drug['drugname'].nunique(),
    'unique_reactions':   reac['pt'].nunique(),
    'glp1_reports':       ps_drug['is_glp1'].sum(),
    'offlabel_reports':   reac['is_offlabel'].sum(),
}])

kpis.to_csv(f'{OUT_DIR}/faers_kpis.csv', index=False)
print("Saved faers_kpis.csv")
print(kpis.T)


# ── CELL 18: OUTPUT — Reporter x Outcome (Dashboard 2, H5) ───────────────────

reporter_outc = (
    master
    .groupby(['reporter_type', 'worst_outcome'])
    .size()
    .reset_index(name='count')
)
reporter_outc.to_csv(f'{OUT_DIR}/faers_reporter_outcome.csv', index=False)
print(f"Saved faers_reporter_outcome.csv ({len(reporter_outc):,} rows)")
print(reporter_outc.pivot_table(index='reporter_type', columns='worst_outcome',
                                 values='count', fill_value=0))


# ── CELL 19: OUTPUT — Age x Outcome (Dashboard 2, H4) ────────────────────────

age_outc = (
    master
    .groupby(['age_grp_label', 'worst_outcome'])
    .size()
    .reset_index(name='count')
)
age_outc.to_csv(f'{OUT_DIR}/faers_age_outcome.csv', index=False)
print(f"Saved faers_age_outcome.csv ({len(age_outc):,} rows)")

# Show missingness so we know if it's usable
unknown_pct = (master['age_grp_label'] == 'Unknown').mean() * 100
print(f"\nAge group missingness: {unknown_pct:.1f}% Unknown")


# ── CELL 20: OUTPUT — Off-label comparison (Dashboard 2, H6) ─────────────────

offlabel_ids = set(reac[reac['is_offlabel']]['primaryid'])
master['offlabel_flag'] = master['primaryid'].isin(offlabel_ids)
master['offlabel_flag'] = master['offlabel_flag'].map({True: 'Off-Label', False: 'On-Label'})

offlabel_outc = (
    master
    .groupby(['offlabel_flag', 'worst_outcome'])
    .size()
    .reset_index(name='count')
)

# Add percentage within each group
totals = master['offlabel_flag'].value_counts().rename('group_total')
offlabel_outc = offlabel_outc.merge(totals, left_on='offlabel_flag', right_index=True)
offlabel_outc['pct'] = (offlabel_outc['count'] / offlabel_outc['group_total'] * 100).round(2)

offlabel_outc.to_csv(f'{OUT_DIR}/faers_offlabel_comparison.csv', index=False)
print(f"Saved faers_offlabel_comparison.csv")
print(offlabel_outc.pivot_table(index='offlabel_flag', columns='worst_outcome',
                                 values='pct', fill_value=0).round(1))


# ── CELL 21: OUTPUT — GLP-1 outcomes (Dashboard 3) ───────────────────────────

glp1_ps = ps_drug[ps_drug['is_glp1']][['primaryid', 'drugname', 'route']].copy()

glp1_outc = glp1_ps.merge(worst_outc, on='primaryid', how='left')
glp1_outc['worst_outcome'] = glp1_outc['worst_outcome'].fillna('No Outcome Reported')
glp1_outc.to_csv(f'{OUT_DIR}/glp1_outcomes.csv', index=False)
print(f"Saved glp1_outcomes.csv ({len(glp1_outc):,} rows)")
print("\nGLP-1 outcomes:")
print(glp1_outc['worst_outcome'].value_counts())


# ── CELL 22: OUTPUT — GLP-1 reactions (Dashboard 3) ──────────────────────────

glp1_reac = glp1_ps.merge(reac[['primaryid', 'pt', 'is_dosing_error']], on='primaryid', how='left')
glp1_reac.to_csv(f'{OUT_DIR}/glp1_reactions.csv', index=False)
print(f"Saved glp1_reactions.csv ({len(glp1_reac):,} rows)")
print("\nTop 20 GLP-1 reactions:")
print(glp1_reac['pt'].value_counts().head(20))


# ── CELL 23: OUTPUT — GLP-1 demographics (Dashboard 3) ───────────────────────

glp1_demo = glp1_ps.merge(demo_clean, on='primaryid', how='left')
glp1_demo = glp1_demo.merge(worst_outc, on='primaryid', how='left')
glp1_demo['worst_outcome'] = glp1_demo['worst_outcome'].fillna('No Outcome Reported')
glp1_demo.to_csv(f'{OUT_DIR}/glp1_demographics.csv', index=False)
print(f"Saved glp1_demographics.csv ({len(glp1_demo):,} rows)")


# ── CELL 24: OUTPUT — GLP-1 indications (Dashboard 3) ────────────────────────

glp1_indi = glp1_ps.merge(indi[['primaryid', 'indi_pt']], on='primaryid', how='left')
glp1_indi.to_csv(f'{OUT_DIR}/glp1_indications.csv', index=False)
print(f"Saved glp1_indications.csv ({len(glp1_indi):,} rows)")
print("\nTop 15 GLP-1 indications:")
print(glp1_indi['indi_pt'].value_counts().head(15))


# ── CELL 25: OUTPUT — GLP-1 dosing errors vs all drugs (Dashboard 3, H2) ─────

# Dosing error rate for GLP-1 cases
glp1_ids = set(glp1_ps['primaryid'])
reac['is_glp1_case'] = reac['primaryid'].isin(glp1_ids)

dosing_summary = (
    reac
    .groupby('is_glp1_case')
    .agg(
        total_reactions=('primaryid', 'count'),
        dosing_errors=('is_dosing_error', 'sum')
    )
    .reset_index()
)
dosing_summary['dosing_error_pct'] = (
    dosing_summary['dosing_errors'] / dosing_summary['total_reactions'] * 100
).round(2)
dosing_summary['group'] = dosing_summary['is_glp1_case'].map(
    {True: 'GLP-1 Drugs', False: 'All Other Drugs'}
)

dosing_summary.to_csv(f'{OUT_DIR}/glp1_dosing_vs_all.csv', index=False)
print("Saved glp1_dosing_vs_all.csv")
print(dosing_summary[['group', 'total_reactions', 'dosing_errors', 'dosing_error_pct']])


# ── CELL 26: OUTPUT — GLP-1 therapy duration (Dashboard 3) ───────────────────

glp1_ther = glp1_ps.merge(ther[['primaryid', 'start_dt', 'end_dt', 'duration_days']],
                           on='primaryid', how='left')
glp1_ther_valid = glp1_ther[glp1_ther['duration_days'].notna() &
                              (glp1_ther['duration_days'] >= 0) &
                              (glp1_ther['duration_days'] <= 3650)]

glp1_ther_valid.to_csv(f'{OUT_DIR}/glp1_therapy_duration.csv', index=False)
print(f"Saved glp1_therapy_duration.csv ({len(glp1_ther_valid):,} valid rows)")
print(f"Coverage: {len(glp1_ther_valid)/len(glp1_ps)*100:.1f}% of GLP-1 cases have duration data")
print(glp1_ther_valid['duration_days'].describe())


# ── CELL 27: Final summary ────────────────────────────────────────────────────

print("=" * 50)
print("ALL OUTPUT FILES SAVED")
print("=" * 50)
for f in sorted(os.listdir(OUT_DIR)):
    fpath = os.path.join(OUT_DIR, f)
    size_kb = os.path.getsize(fpath) / 1024
    print(f"  {f}: {size_kb:.0f} KB")
