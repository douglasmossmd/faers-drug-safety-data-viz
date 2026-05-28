# FAERS Drug Safety Dashboard
### BUS 32130: Data Visualization for Decision-Making — Final Project
**Douglas Moss & Livie Anastasya, Booth School of Business, Spring 2026**

---

## Project Overview

This project analyzes the **FDA Adverse Event Reporting System (FAERS)**, the FDA's post-market drug safety surveillance database, using all four quarters of 2025 data (Q1 through Q4). The output is a three-part Tableau visualization suite plus a standalone web-based drug lookup tool we built in HTML/JavaScript.

The question we wanted to answer: what does real-world drug safety data actually tell us, and can any of it be turned into something a clinician would use?

As an emergency physician, I see patients every day whose symptoms might be drug-related. FAERS captures that kind of post-market adverse event data at massive scale. Clinical trials are run under tight conditions; FAERS is what actually happens when millions of people take a drug in the real world. We wanted to surface those signals without dressing them up.

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

We started with six hypotheses and tested each against the cleaned dataset. The results were mixed, and we kept them that way (a couple of the "non-findings" are arguably more interesting than the confirmations).

| Hypothesis | Finding | Supported? |
|---|---|---|
| High-volume drugs ≠ most dangerous | Dupixent (#1 by volume, 0.38% death rate) vs. Humira (6.37%), Revlimid (5.59%) | ✅ Yes |
| GLP-1 drugs show disproportionate dosing errors | GLP-1 dosing error rate: 10.55% vs. 1.92% for all other drugs (5.5× higher) | ✅ Yes |
| Consumer reporting dominates lifestyle drugs | GLP-1 consumer reporting confirmed; complex therapeutics physician-dominated | ✅ Partial |
| Elderly patients have worse outcomes | Age data 64.2% missing — insufficient coverage for strong conclusions | ⚠️ Inconclusive |
| Physician reports associated with worse outcomes | Physician-reported cases: 11.16% death rate vs. 4.39% for consumer reports | ✅ Yes |
| Off-label use → worse outcomes | Off-label death rate: 7.4% vs. on-label: 7.5% — no meaningful difference | ❌ Not supported |

The off-label null finding is interesting in its own right. Out of 107,825 off-label reports, outcomes were statistically indistinguishable from on-label use, at least inside FAERS.

---

## Caveats

A few things to keep in mind when reading any of the numbers above:

- FAERS is voluntary. It records what gets reported, not what actually happens in the world, and under-reporting is heaviest for mild events.
- Report volume tracks prescribing popularity more than danger. A drug with 100,000 reports is usually just widely prescribed.
- No causality is established here. A reported event after drug use is not the same as the drug causing it.
- 64.2% of age records are missing in the 2025 data. Treat any age-based slice with caution.
- Drug name standardization is imperfect. We uppercased everything and mapped GLP-1s by hand, but spelling variants and abbreviations almost certainly cause some undercounting elsewhere.
- GLP-1 therapy-duration coverage is only 22% of cases. That dataset is included but should not be the basis of strong claims.

---

## Dashboard Structure

### Dashboard 1: Scale and the Volume-vs-Danger Paradox
What does 2025 drug safety data look like at a glance, and do the most-reported drugs actually carry the most risk?

- KPI tiles: total reports, deaths, hospitalizations, GLP-1 share
- Top Drugs by Volume (bar chart)
- Volume vs. Danger scatter (report count against death rate; this is where the paradox lives)
- Top Reactions globally
- Quarterly Trend (outcome mix across Q1–Q4)
- World Map (reporting geography)

### Dashboard 2: Who's Reporting, and Does It Shift the Picture?
Does the identity of the reporter change the safety signal?

- Reporter Type × Death Rate (physicians tend to report the serious stuff)
- Who Is Reporting (breakdown by reporter type)
- Off-Label vs. On-Label Outcomes (the null finding, left as-is)
- Age Group × Outcome (with the missingness caveat called out)

### Dashboard 3: The GLP-1 Story
What does adverse event data actually say about the drugs everyone is talking about right now?

- GLP-1 Outcomes by Drug Family
- Top Clinical Reactions (filtering out dosing/administrative terms)
- Dosing Error Rate: GLP-1 vs. All Other Drugs
- Top Prescribing Indications (weight control now exceeds diabetes)
- Drug Family Breakdown (Tirzepatide vs. Semaglutide vs. others)
- Therapy Duration Distribution

### Drug Safety Explorer (web app)
A standalone HTML tool that sits on top of the cleaned FAERS outputs. Search any of the 300 most-reported drugs and you get the same view every time: total reports, death rate, hospitalization rate, outcome breakdown, and the top reported adverse reactions. GLP-1 drugs get an extra section that adds the dosing-error comparison and the prescribing-indication breakdown. The whole thing was designed with a "would this be useful at the bedside?" filter, since that's the actual audience. Redesigned in May 2026 to match the visual language of the static dashboards — navy chrome, ColorBrewer Blues palette, search-first hero landing, and a baseline-comparison chart that shows the drug's death rate against the FAERS-wide 7.52% mean.

---

## Use of AI / LLMs

Per the course requirements, here is where AI tools sat in this project.

We used Claude (Anthropic) throughout, mainly as a coding partner. Specifically:

- Python code for the cleaning pipeline — deduplication, severity ranking, the per-drug aggregations that produced the CSVs in `output_clean/`.
- Debugging the Jupyter notebook when joins or groupbys didn't behave.
- The Drug Safety Explorer web app: HTML, CSS, JavaScript, and the Chart.js wiring. The visual structure was iterated by hand; Claude generated the boilerplate.
- A first pass on this README, which we then rewrote in our own voice.

What we did ourselves: every hypothesis was written down before we ran the analysis, not after. The deduplication logic (keep highest `primaryid` per `caseid`), the severity ladder used to assign one outcome per case, and the choice to restrict drug-level analysis to primary-suspect records were all decisions we made and re-checked against the data. The off-label null result was left alone rather than reframed into a finding.

The cleaning notebook (`faers_cleaning.ipynb`) and the web app (`drug_safety_explorer.html`) are both in this repo, in full.

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
