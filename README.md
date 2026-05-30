# FAERS Drug Safety Dashboard
### BUS 32130: Data Visualization for Decision-Making Final Project
**Douglas Moss & Livie Anastasya, Booth School of Business, Spring 2026**

---

## Project Overview

This project analyzes the **FDA Adverse Event Reporting System (FAERS)**, the FDA's post-market drug safety surveillance database, using all four quarters of 2025 data (Q1 through Q4). The output is a three-part Tableau visualization suite plus a standalone web-based drug lookup tool we built in HTML/JavaScript.

The question we wanted to answer: what does real-world drug safety data actually tell us, and can any of it be turned into something a clinician would use?

As an emergency physician, I see patients every day whose symptoms might be drug-related. FAERS captures that kind of post-market adverse event data at massive scale. Clinical trials are run under tight conditions; FAERS is what actually happens when millions of people take a drug in the real world. We wanted to surface those signals without dressing them up.

---

## Audience & the Questions We Answer

**Primary audience: practicing clinicians**, and specifically the clinicians who already have a stake in this drug class. Think of an endocrinologist fielding a wave of GLP-1 requests, a primary-care physician deciding whether a patient's nausea is the drug or something else, or an emergency physician seeing an adverse event and trying to place it. These are people who read the medical literature but rarely have time to pull raw FAERS files themselves. They want a fast, honest read on a drug's real-world safety profile, not a regulator's full statistical model and not a marketing deck.

We designed for that reader on two levels, because clinicians don't all consume data the same way:

- **The dashboards** are for the clinician who wants the landscape — the five-panel story of what 2025 adverse-event data looks like across the whole drug supply and the GLP-1 class in particular. You read these the way you'd read a journal figure.
- **The web portal** is for the clinician at the point of care who has one drug in mind and ten seconds to spare. You type the name, you get the profile. Same data, different entry point.

Secondary readers — pharmacovigilance staff, health-policy researchers, and frankly any informed patient on one of these drugs — get value from the same artifacts without any of them being the design target. We optimized for the clinician and let everyone else benefit.

Every artifact answers four concrete questions for that audience:

1. **Does report *volume* equal *danger*?** (The most-reported drug is rarely the most lethal.)
2. **Does *who reports* change the safety signal?** (Physician vs. consumer reporting.)
3. **What does the data actually say about GLP-1 drugs** — the class everyone is currently prescribing for weight loss?
4. **Can a clinician look up a single drug and get a trustworthy profile at the bedside in under ten seconds?**

The first three are answered by the static Tableau/Plotly/Excel dashboards; the fourth is answered by the interactive Drug Safety Explorer web portal. Relevance to the audience drove every design choice. We kept clinical reaction terms instead of dumbing them down, surfaced death and hospitalization rates first because that is what a prescriber checks first, and put every caveat directly on the graph so the visuals stand alone without narration.

---

## Our Thought Process & Assumptions

We did not start with a chart and look for a reason to build it. We started with a point of view: that the public conversation about drug safety, and GLP-1s especially, runs on volume and vibes rather than on what the post-market data actually shows. FAERS is the closest thing to a ground truth for real-world adverse events, so the plan was to let it either confirm or puncture the conventional wisdom and to report whichever way it landed.

The sequence we worked in:

1. **Write the hypotheses first.** All six hypotheses in the table below were committed to before we ran a single aggregation. This was deliberate — it kept us from p-hacking our way into a tidy story and made the off-label null result something we had to publish rather than something we could quietly drop.
2. **Clean before we trust.** Roughly 1.6M raw records do not become 1.5M clean ones for free. The deduplication, worst-outcome ranking, and primary-suspect filtering (detailed in *Data Cleaning & Processing*) were the load-bearing decisions; every downstream number inherits them.
3. **Validate in a second tool.** We rebuilt the headline figures in Excel independently of the Python pipeline. When the two agreed, we trusted the number; when they did not, we found the join bug. Two tools, one answer.
4. **Design last.** Only once the numbers were stable did we move into Tableau, Plotly, and Inkscape. Polishing a chart that is built on a bad aggregation is wasted effort.

**The assumptions we are making explicit, because they shape every figure:**

- **A report is a signal, not a verdict.** FAERS records that an event was *reported* after a drug was taken, not that the drug *caused* it. We treat counts as signals worth investigating, never as proof of causation.
- **The most recent submission is the truth.** When a case appears multiple times, we keep the highest `primaryid` and assume later follow-ups supersede earlier ones.
- **One case, one worst outcome.** A patient who is hospitalized and then dies is counted once, as a death, via a fixed severity ladder. This understates total event counts but prevents double-counting deaths.
- **Primary-suspect only, for drug-level claims.** When we attribute an event to a drug, we use only records where that drug was coded the primary suspect, not a concomitant medication the patient happened to be on.
- **Brand and generic are the same drug.** Ozempic, Wegovy, and Rybelsus all roll up to semaglutide. We mapped the GLP-1 family by hand and assume the mapping is complete for this class; we make no such guarantee for the long tail of other drugs.
- **Reporting geography ≠ where the event happened.** Reporter country is where the report originated, which over-weights the United States and should not be read as global incidence.

The flip side of these assumptions — what they prevent us from claiming — is documented honestly in the **Caveats** section further down. We would rather a clinician trust a smaller number than over-read a bigger one.

---

## Deliverables

| Artifact | Description |
|---|---|
| **Tableau Workbooks** | `.twbx` packaged workbooks behind the Overview, Reporter-Patterns, GLP-1, and Quarterly-Trend analyses |
| **Final Dashboards** | 5 design-polished dashboards composited in Inkscape (`inkscape final dashboards/`) |
| **Chart Exports** | 26 source SVGs from Tableau, Plotly, and Matplotlib (`svg files/`) |
| **Excel Workbook** | 11-sheet cross-check workbook with charts, graphs and heatmaps|
| **Drug Safety Explorer** | Standalone interactive web portal — search any drug, instant safety profile |
| **Data Pipeline** | Jupyter notebook + Python scripts for all data cleaning and processing |

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

## From Data to Dashboard — The Visualization Process

The cleaned CSVs in `data/` were never the deliverable; they were the raw material. Turning ~1.5M rows of adverse-event data into five dashboards that *stand alone without narration* took a deliberate, multi-tool pipeline. Each tool was chosen for what it is genuinely good at — "clever" for its own sake was avoided, because complexity that doesn't serve the clinical question gets in the reader's way.

```
Cleaned CSVs (Python/pandas)
        │
        ├──►  Tableau          ──►  .svg exports   ┐
        ├──►  Python / Plotly  ──►  .svg exports   ├──►  Inkscape  ──►  5 final dashboards (.png)
        ├──►  Python / Matplotlib ─►  .svg/.png    ┘                         │
        └──►  Excel            ──►  charts .svg exports                      │
                                                                             ▼
                              Drug Safety Explorer  ──►  high-fidelity HTML prototype (GitHub Pages)
```

### Stage 1 — Build the charts in Tableau (primary tool)

Tableau is the backbone of the project and the primary visualization tool, as required. Two packaged workbooks are committed so the work is fully reproducible:

| File | What it contains |
|---|---|
| `FAERS and GLP-1_DataViz.twbx` | The main workbook — all worksheets behind the Overview, Reporter-Patterns, and GLP-1 dashboards |
| `FAERS and GLP-1 Quarterly Trends.twbx` | Focused workbook for the Q1–Q4 outcome-mix trend analysis |

Inside Tableau we built the worksheets that needed real interaction and geographic/statistical handling — the **volume-vs-danger scatter**, the **quarterly outcome-mix trend**, the **world map** of reporting geography, and the GLP-1 family breakdowns. Correct Tableau technique mattered here: calculated fields for death/hospitalization rates, level-of-detail expressions to assign one worst-outcome per case, and dual-axis work for the comparison charts. Finished worksheets were exported as **vector SVG** (Tableau → Worksheet → Export → Image/SVG) so nothing degrades when rescaled. These exports live in `svg files/` as the title-cased files — `Age vs Outcome.svg`, `GLP1 Drug Breakdown.svg`, `GLP1 Indications.svg`, `GLP1 Outcomes.svg`, and `Off Label Outcomes.svg`.

### Stage 2 — Static charts in Python (Plotly + Matplotlib)

For the charts that needed pixel-precise control or repetitive small-multiples, we generated them programmatically in Python directly off the cleaned CSVs. **Plotly** produced the majority of the static panels — its SVG export (recognisable by the `class="main-svg"` signature) gave us clean, editable vectors. These are the `tab*`, `top10_*`, `family_grid`, `teaser_*`, `top20_reactions`, and distribution files in `svg files/`, including:

- `tab3_volume_vs_danger.svg`, `tab6_quarterly_trend.svg`, `tab7_outcome_mix.svg`, `tab10_offlabel_vs_onlabel.svg`, `tab11_world_map.svg` — the analytical panels
- `top10_semaglutide.svg`, `top10_tirzepatide.svg`, `top10_liraglutide.svg`, `top10_dulaglutide.svg`, `top10_exenatide.svg` — per-drug small multiples
- `family_grid.svg`, `top20_reactions.svg`, `top15_serious_allfaers.svg`, `age_buckets.svg`, `sex_distribution.svg` — supporting breakdowns

Generating with code (rather than clicking) meant the GLP-1 family small-multiples shared an identical axis, scale, and palette automatically — a Gestalt **similarity/uniformity** win that would have been tedious to enforce by hand.

### Stage 3 — Excel as a cross-check and second visual source

`FAERS_2025_Excel_Visualizations.xlsx` is a full Excel workbook (11 tabbed sheets, 8 native charts) that mirrors the analysis: `Overview`, `Top Drugs`, `Volume vs Danger`, `Top Reactions`, `Drug-Reaction Heat`, `Quarterly Trend`, `Outcome Mix`, `Reporter Mix`, `Age x Outcome`, `Off- vs On-Label`, and `Countries`. Excel served two purposes: (1) it satisfies the rubric's Python-**OR**-Excel integration requirement and (2) it acted as an independent sanity check — building the same numbers in a second tool caught a join error before it reached the final art. PivotTable-driven, the workbook is the "show your work" companion to the polished dashboards and also created several charts that tableau could not achieve.

### Stage 4 — Export everything to SVG (one common vector format)

Tableau, Plotly, Excel and Matplotlib all funnel into the same format: **SVG**. This was deliberate. SVG is resolution-independent, and — critically — every element (text, bar, axis, color swatch) remains an *editable object*. That made the next stage possible. All 26 exports are collected in `svg files/` as the single staging directory between "charting" and "design." We did not end up using everything on our actual dashboards but we picked the ones that are most relevant.

### Stage 5 — Composite & polish in Inkscape (professional design pass)

The raw exports were good analysis but not yet good *design*. Each SVG was imported into **Inkscape** (free, open-source vector editor) and composited into five cohesive dashboards. This is where the project moves from "charts" to "designed artifacts," and where the **Principles of Good Design** rubric (and its Inkscape/Illustrator bonus) is earned. The five finished dashboards are in `inkscape final dashboards/`:

| Dashboard | File | Question it answers |
|---|---|---|
| 1 · Overview | `dashboard_1_overview_inkscape.png` | Scale of 2025 FAERS + the volume-vs-danger paradox |
| 2 · Patterns | `dashboard_2_patterns.png` | Who reports, and does it shift the signal? |
| 3 · GLP-1 | `dashboard_3_glp1.png` | The GLP-1 deep dive |
| 4 · Details | `dashboard_4_details.png` | Drill-down detail panels |
| 5 · Takeaways | `dashboard_5_takeaways.png` | Plain-language conclusions for the clinician |

See the **Design Principles** section below for exactly what changed in Inkscape.

### Stage 6 — The interactive web portal (high-fidelity prototype)

The static dashboards answer the "big picture" questions. The fourth question — *can a clinician look up one drug at the bedside?* — needed something interactive, so we built the **Drug Safety Explorer** as a standalone, single-file HTML web app (`drug_safety_explorer.html`). It sits on top of the same cleaned FAERS outputs: search any of the 300 most-reported drugs and get an instant profile (total reports, death rate, hospitalization rate, outcome breakdown, top reactions, and — for GLP-1s — the dosing-error and indication comparisons), with a baseline marker showing the drug's death rate against the FAERS-wide 7.52% mean.

It is a genuine **high-fidelity prototype**: production-quality look and feel, real data, real interactivity, deployed to a public URL via **GitHub Pages** so it runs in any browser with no install. We built it with Claude as a coding partner — Claude generated the HTML/CSS/JavaScript and the interactive charting scaffold while we directed the visual structure, the clinical framing, and every design decision and the data we wanted to include. The charts are rendered with **Chart.js**; the visual language (navy chrome, ColorBrewer Blues palette, search-first hero) was deliberately matched to the static Inkscape dashboards so the whole suite reads as one product.

**Live:** https://douglasmossmd.github.io/faers-drug-safety-data-viz/drug_safety_explorer.html

---

## Design Principles on Inkscape

### Color theory
- A single restrained palette across **all** artifacts — a **navy + ColorBrewer Blues** sequential scheme — so the eye reads intensity, not rainbow noise. Sequential blues encode magnitude (more reports / higher rate = deeper blue) honestly, without implying false categories. We also wanted to invoke a medical/clinical color palette because that was our main audience/
- Backgrounds and chrome are low-saturation neutrals so the data has the highest contrast on the page (figure/ground).

### Gestalt principles
- **Proximity & common region:** related KPIs and their explanatory text are grouped inside shared cards/panels, so the reader parses the dashboard as a few meaningful blocks rather than a wall of charts.
- **Similarity:** the five GLP-1 per-drug small-multiples share identical axes, scale, and color, so they're instantly comparable — differences in the *data* pop because the *form* is uniform.
- **Alignment & continuity:** a strict underlying grid in Inkscape; titles, axes, and panels snap to common baselines, which is what makes the composite look "designed" rather than pasted.
- **Figure/ground:** caveats and annotations sit in muted secondary type so they're present but never compete with the headline number.

### Typeface selection
- A two-tier type system: one clean **sans-serif for all UI/labels/data** (legibility at small sizes, the clinical-instrument feel we wanted) with weight — not font-switching — used to build hierarchy (bold headline number, regular label, light caveat). Consistent type across the Tableau exports, the Inkscape dashboards, and the web portal is what makes the artifacts read as one family.

### Data storytelling & restraint
- Every dashboard leads with the *question*, not the chart type, and ends (Dashboard 5) with plain-language takeaways.
- Per the brief's note on complexity, we deliberately *avoided* clever visualizations: no 3-D, no dual-encoded novelty charts. The volume-vs-danger scatter is "just" a scatter because the scatter is the clearest way to show that volume ≠ danger. Complexity was only kept where it served the clinical question.
- Null findings (off-label outcomes) are shown as-is rather than reframed — honest storytelling over a tidy narrative.

---

## Why This Is a Data Story — and Why This Format

This project is a data story, not a data dump, and the distinction is the whole point. Underneath the GLP-1 counts and death rates is a story about a population: millions of real patients in 2025, a drug class moving from diabetes wards into weight-loss clinics, and a pattern of dosing errors that shows up the moment a complex injectable lands in less-supervised hands. The data is the vehicle; the patient population is the subject. Every dashboard is built to advance that narrative — from "here is the scale of what we are looking at," to "here is who is reporting and what GLP-1s are actually doing," to a closing panel of plain-language takeaways a clinician can act on.

**Why two formats instead of one.** We deliberately split the deliverable into static dashboards and an interactive portal because the story has two natural reading modes, and forcing both into one artifact would have served neither.

- A **linear, designed dashboard sequence** is the right format for the *argument*. Stories need an order, and a curated five-panel flow lets us control pacing: set up the volume-vs-danger paradox before resolving it, introduce the reporter-bias lens before the GLP-1 deep dive, and land on takeaways last. An interactive tool cannot enforce that arc, because the user clicks wherever they want.
- A **search-first interactive portal** is the right format for the *lookup*. The bedside question — "what do I need to know about *this* drug, right now" — is inherently non-linear and personal to whatever the clinician just prescribed. A static PDF could never answer it for all 300 drugs; a database with a search box answers it in seconds.

Put differently: the dashboards make the case, and the portal lets the reader interrogate it. Choosing one format would have meant either a beautiful story nobody could query or a useful tool with no argument. The two formats are not redundant — they are the same data told at two altitudes, and that is what makes the whole thing serve its goal.

We also made a conscious choice *against* spectacle. The flashiest version of this project would have leaned on animated network graphs and novelty encodings. We did not, because a clinician deciding whether to worry about a patient's symptom is not looking to be impressed — they are looking to be informed quickly and correctly. The restraint *is* the storytelling approach.

---

## Use of AI / LLMs

Per the course requirements, here is where AI tools sat in this project.

We used Claude (Anthropic) throughout, mainly as a coding partner. Specifically:

- Python code for the cleaning pipeline — deduplication, severity ranking, the per-drug aggregations that produced the CSVs in `data/`.
- Debugging the Jupyter notebook when joins or groupbys didn't behave.
- The Python/Plotly and Matplotlib charting scripts that exported the static SVG panels in `svg files/`.
- The Drug Safety Explorer web app: HTML, CSS, JavaScript, and the Chart.js wiring, plus help publishing it to GitHub Pages as a high-fidelity prototype. The visual structure was iterated by hand; Claude generated the boilerplate.
  
What stayed fully human: all chart *design* decisions, the Tableau worksheet construction, the Inkscape compositing pass and how we analyzed and interpreted the data.

What we did ourselves: every hypothesis was written down before we ran the analysis, not after. The deduplication logic (keep highest `primaryid` per `caseid`), the severity ladder used to assign one outcome per case, and the choice to restrict drug-level analysis to primary-suspect records were all decisions we made and re-checked against the data. The off-label null result was left alone rather than reframed into a finding.

The cleaning notebook (`faers_cleaning.ipynb`) and the web app (`drug_safety_explorer.html`) are both in this repo, in full.

---

## Tools Used

| Tool | Purpose |
|---|---|
| Python (pandas) | Data cleaning, aggregation, output generation |
| Jupyter Notebook | Interactive data pipeline |
| Tableau | Primary visualization tool — scatter, heatmap, trends, map, GLP-1 worksheets (`.twbx` workbooks → SVG) |
| Python (Plotly) | Static analytical panels and per-drug small-multiples, exported to SVG |
| Python (Matplotlib) | Supporting static figures |
| Excel | Independent cross-check workbook, graphs, heatmaps and charts (`FAERS_2025_Excel_Visualizations.xlsx`) |
| Inkscape | Vector compositing and design polish → 5 final dashboards |
| HTML / CSS / JavaScript | Drug Safety Explorer web portal (high-fidelity prototype) |
| Chart.js | Interactive charts within the web portal |
| GitHub Pages | Hosting the live web portal |
| GitHub | Version control and submission |

---

## Repository Structure

```
├── README.md                                  ← This file
├── faers_cleaning.ipynb                       ← Full data cleaning pipeline
├── snippets.py                                ← Cleaning code reference (plain Python)
├── drug_safety_explorer.html                  ← Interactive web portal (high-fidelity prototype)
├── FAERS and GLP-1_DataViz.twbx               ← Main Tableau packaged workbook
├── FAERS and GLP-1 Quarterly Trends.twbx      ← Tableau quarterly-trend workbook
├── FAERS_2025_Excel_Visualizations.xlsx       ← Excel cross-check workbook (11 sheets, 8 charts)
├── data/                                       ← All processed CSV outputs (the 17 cleaned files)
├── svg files/                                  ← 26 chart exports: Tableau (title-cased) + Plotly/Matplotlib (tab*, top10*, …)
└── inkscape final dashboards/                  ← 5 composited, design-polished dashboards (.png)
    ├── dashboard_1_overview_inkscape.png
    ├── dashboard_2_patterns.png
    ├── dashboard_3_glp1.png
    ├── dashboard_4_details.png
    └── dashboard_5_takeaways.png
```

---

*Data: FDA FAERS 2025 Q1–Q4 · Last updated May 2026 · Douglas Moss & Livie Anastasya*
