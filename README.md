# FAERS Drug Safety Dashboard
### BUS 32130: Data Visualization for Decision-Making — Final Project
**Douglas Moss & Livie Anastasya · Booth School of Business · Spring 2026**

---

## Project Overview

This project analyzes the **FDA Adverse Event Reporting System (FAERS)** — the FDA's post-market drug safety surveillance database — using all four quarters of 2025 data (Q1–Q4). The result is a three-part interactive visualization suite built in Tableau, supplemented by an original web-based drug safety lookup tool built from scratch in HTML/JavaScript.

The central question: *What does real-world drug safety data actually tell us — and can it be made actionable for clinicians?*

As an emergency physician, I see patients daily whose symptoms may be drug-related. FAERS captures exactly this kind of real-world adverse event data at massive scale. Unlike clinical trial data collected under controlled conditions, FAERS reflects what actually happens when drugs are used by millions of patients in practice. This project attempts to surface those signals clearly and honestly.

---

## Deliverables

| Artifact | Description |
|---|---|
| **Tableau Workbook** | Three dashboards: Overview, Reporter Patterns, and GLP-1 Deep Dive |
| **Drug Safety Explorer** | Standalone interactive web app — search any drug, instant safety profile |
| **Data Pipeline** | Jupyter notebook + Python scripts for all data cleaning and processing |

- 📊 [Tableau Public Workbook](#) *(add link after upload)*
- 🌐 [Drug Safety Explorer — Live App](https://douglasmossmd.github.io/faers-drug-safety-data-viz/drug_safety_explorer.html)

---

## Data Sources

**FDA Adverse Event Reporting System (FAERS)**
- Source: [FDA FAERS](https://www.fda.gov/drugs/questions-and-answers-fdas-adverse-event-reporting-system-faers)
- Quarters: 2025 Q1, Q2, Q3, Q4
- Format: 7 pipe-delimited ASCII text files per quarter

| File | Contents |
|---|---|
| `DEMO` | Patient demographics, reporter country, report date |
| `DRUG` | Drug name, role (primary suspect vs. concomitant), route |
| `REAC` | Adverse reactions using MedDRA terminology |
| `OUTC` | Patient outcomes (death, hospitalization, etc.) |
| `INDI` | Indication — why the drug was prescribed |
| `RPSR` | Report source (consumer, health professional, etc.) |
| `THER` | Therapy start and end dates |

**Scale:** 1,617,444 raw DEMO records across four quarters; 1,469,305 after deduplication.

---

## Data Cleaning & Processing

All cleaning was performed in Python (Jupyter notebook: `faers_cleaning.ipynb`). Key steps:

### 1. Deduplication
FAERS allows follow-up submissions on the same case, meaning one adverse event can appear multiple times across quarters. Cases were deduplicated by `caseid`, retaining the most recent submission (highest `primaryid`). This removed 148,139 duplicate records.

### 2. Drug Name Standardization
Drug names are free-text fields, meaning the same drug can appear as a brand name, generic name, or misspelling. All names were uppercased and stripped of whitespace. GLP-1 drugs were mapped explicitly (e.g., OZEMPIC, SEMAGLUTIDE → same drug family).

### 3. Worst Outcome Logic
Each case can have multiple outcomes (e.g., hospitalized and then died). To avoid double-counting, each case was assigned its single most severe outcome using a severity ranking: Death > Life-Threatening > Hospitalization > Disability > Required Intervention > Congenital Anomaly > Other Serious. Cases with no outcome record were labeled "No Outcome Reported."

### 4. Primary Suspect Only
For drug-level analysis, only drugs coded as the primary suspect (`role_cod = 'PS'`) were included, excluding concomitant medications the patient happened to be taking.

### 5. GLP-1 Classification
GLP-1 receptor agonists were identified by both brand and generic name across five drug families: Semaglutide (Ozempic, Wegovy, Rybelsus), Tirzepatide (Mounjaro, Zepbound), Liraglutide (Victoza, Saxenda), Dulaglutide (Trulicity), and Exenatide.

### 6. Dosing Error Classification
Reactions were flagged as dosing errors if they matched any of: Incorrect dose administered, Extra dose administered, Accidental underdose, Product dose omission issue, Overdose, Underdose.

### Output Files
All cleaned outputs are saved to `FAERS Data/output_clean/`:

| File | Rows | Purpose |
|---|---|---|
| `faers_demographics.csv` | 1,469,305 | Master case table with outcomes |
| `faers_drug_summary.csv` | 300 | Top drugs: report counts, death rates |
| `faers_drug_long.csv` | 2,109 | Outcome breakdown per drug (long format) |
| `faers_drug_reactions.csv` | 3,000 | Top 10 reactions per drug |
| `faers_reaction_summary.csv` | 150 | Top reactions globally |
| `faers_kpis.csv` | 1 | Headline KPI figures |
| `faers_reporter_outcome.csv` | 48 | Reporter type × outcome |
| `faers_age_outcome.csv` | 53 | Age group × outcome |
| `faers_offlabel_comparison.csv` | 16 | Off-label vs. on-label outcomes |
| `faers_quarterly_trend.csv` | 32 | Outcome trends by quarter |
| `faers_country_outcome.csv` | — | Outcome rates by country (81 countries) |
| `glp1_demographics.csv` | 86,839 | GLP-1 cases with full demographics |
| `glp1_outcomes.csv` | 86,839 | GLP-1 outcomes by drug |
| `glp1_reactions.csv` | 204,828 | GLP-1 adverse reactions |
| `glp1_indications.csv` | 276,833 | GLP-1 prescribing indications |
| `glp1_therapy_duration.csv` | 19,111 | GLP-1 therapy duration (valid cases) |
| `glp1_dosing_vs_all.csv` | 2 | Dosing error rate: GLP-1 vs. all other |

---

## Hypotheses & Findings

Six hypotheses were tested against the data. Results were mixed — which is honest, and worth saying.

| Hypothesis | Finding | Supported? |
|---|---|---|
| High-volume drugs ≠ most dangerous | Dupixent (#1 by volume, 0.38% death rate) vs. Humira (6.37%), Revlimid (5.59%) | ✅ Yes |
| GLP-1 drugs show disproportionate dosing errors | GLP-1 dosing error rate: 10.55% vs. 1.92% for all other drugs (5.5× higher) | ✅ Yes |
| Consumer reporting dominates lifestyle drugs | GLP-1 consumer reporting confirmed; complex therapeutics physician-dominated | ✅ Partial |
| Elderly patients have worse outcomes | Age data 64.2% missing — insufficient coverage for strong conclusions | ⚠️ Inconclusive |
| Physician reports associated with worse outcomes | Physician-reported cases: 11.16% death rate vs. 4.39% for consumer reports | ✅ Yes |
| Off-label use → worse outcomes | Off-label death rate: 7.4% vs. on-label: 7.5% — no meaningful difference | ❌ Not supported |

The off-label null finding is itself interesting: despite 107,825 off-label reports, outcomes are statistically indistinguishable from on-label use, at least within FAERS.

---

## Notable Limitations

- **FAERS is a voluntary reporting system.** It captures what gets reported, not what actually occurs. Under-reporting is substantial, especially for mild adverse events.
- **Report volume reflects prescribing popularity, not danger.** A drug with 100,000 reports is likely widely prescribed, not necessarily dangerous.
- **No causality is established.** A reported adverse event following drug use does not mean the drug caused it.
- **64.2% of age records are missing** in the 2025 dataset. Age-based analysis should be interpreted cautiously.
- **Drug name standardization is imperfect.** Despite uppercasing and explicit GLP-1 mapping, spelling variants and abbreviations may still result in undercounting for some drugs.
- **GLP-1 therapy duration coverage is only 22%** of cases, limiting conclusions from that dataset.

---

## Dashboard Structure

### Dashboard 1 — Overview: Scale & the Volume-Danger Paradox
*Question: What does 2025 drug safety data look like, and do the most-reported drugs carry the most risk?*

- KPI tiles: total reports, deaths, hospitalizations, GLP-1 share
- Top Drugs by Volume (bar chart)
- Volume vs. Danger scatter (report count vs. death rate — the paradox lives here)
- Top Reactions globally
- Quarterly Trend (outcome mix across Q1–Q4)
- World Map (reporting geography)

### Dashboard 2 — Patterns: Who's Reporting, and Does It Change What We See?
*Question: Does the identity of the reporter shape the safety signal?*

- Reporter Type × Death Rate (physicians report the serious stuff)
- Who Is Reporting (breakdown by reporter type)
- Off-Label vs. On-Label Outcomes (the null finding — honestly presented)
- Age Group × Outcome (with explicit missingness caveat)

### Dashboard 3 — The GLP-1 Story
*Question: What does adverse event data actually say about the drugs everyone is talking about?*

- GLP-1 Outcomes by Drug Family
- Top Clinical Reactions (filtering out dosing/administrative terms)
- Dosing Error Rate: GLP-1 vs. All Other Drugs
- Top Prescribing Indications (weight control now exceeds diabetes)
- Drug Family Breakdown (Tirzepatide vs. Semaglutide vs. others)
- Therapy Duration Distribution

### Drug Safety Explorer (Web App)
An interactive, standalone HTML tool built entirely from the processed FAERS data. Search any of the 300 most-reported drugs and instantly see: total reports, death rate, hospitalization rate, outcome breakdown, and top adverse reactions. GLP-1 drugs receive an enhanced profile including dosing error comparison and indication breakdown. Designed with a clinical context in mind — what would actually be useful at the bedside?

---

## Use of AI / LLMs

Per course requirements, AI tools were used throughout this project. Their role was assistive and is documented here:

- **Claude (Anthropic)** was used extensively for:
  - Python code generation for data cleaning, deduplication, and output file creation
  - Iterative debugging of the Jupyter notebook
  - Building the Drug Safety Explorer web app (HTML, CSS, JavaScript, Chart.js integration)
  - Drafting this README
  - Narrative structuring and hypothesis framing

- **Judgment and interpretation remained mine.** All hypotheses were defined before analysis. Data quality decisions (deduplication logic, severity ranking, primary-suspect filtering) were made and verified by me. The null finding on off-label use was not smoothed over or reframed.

- The cleaning notebook (`faers_cleaning.ipynb`) and the web app (`drug_safety_explorer.html`) are both included in this repository and can be inspected in full.

---

## Tools Used

| Tool | Purpose |
|---|---|
| Python (pandas) | Data cleaning, aggregation, output generation |
| Jupyter Notebook | Interactive data pipeline |
| Tableau | Primary visualization (Dashboards 1–3) |
| HTML / CSS / JavaScript | Drug Safety Explorer web app |
| Chart.js | Charts within the web app |
| GitHub | Version control and submission |

---

## Repository Structure

```
├── README.md                          ← This file
├── faers_cleaning.ipynb               ← Full data cleaning pipeline
├── snippets.py                        ← Cleaning code reference (plain Python)
├── drug_safety_explorer.html          ← Interactive drug lookup tool
├── Final Draft w GLP1.twb             ← Tableau workbook (main)
├── FAERS and GLP-1_DataViz.twbx       ← Tableau packaged workbook
└── FAERS Data/
    ├── Untouched/                     ← Raw FDA downloads (Q1–Q4)
    └── output_clean/                  ← All processed CSV outputs
```

---

*Data: FDA FAERS 2025 Q1–Q4 · Last updated May 2026 · Douglas Moss & Livie Anastasya*
