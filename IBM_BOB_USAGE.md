# IBM Bob — AI Assistant Contribution Log

**Project:** AI Email Campaign Automation Agent  
**Hackathon Submission**  
**AI Coding Assistant:** IBM Bob (Agent Mode)

---

## Overview

IBM Bob was used as the primary AI coding assistant throughout the development of this project. This document records the specific work Bob performed, following the workflow:

**Analysis → Planning → Implementation → Testing → Documentation**

---

## 1. Initial Project Analysis

Bob examined the existing project artefacts to establish a baseline before writing any code:

- Read and analysed `main.ipynb` to understand the customer segmentation logic, feature engineering steps (Age, Total_Purchases, Total_Spent, Customer_Value), and the segmentation thresholds used in notebook cell 18 (`>= 5000` → Medium, `>= 15000` → High).
- Inspected `marketing_campaign.csv` to identify the dataset structure: 29 columns including `Year_Birth`, `Income`, `Mnt*` product spend columns, `Num*Purchases` channel columns, and `Recency`.
- Identified that the raw CSV uses tab-separated values (not comma), which required a robust CSV loader.
- Confirmed the required output files: `app.py` (Streamlit UI), `gemini.py` (LLM interface), `database.py` (persistence), and `requirements.txt`.

---

## 2. Implementation Planning

Before writing code Bob established the architecture:

- **`gemini.py`** — thin wrapper around the OpenRouter API using the `openai` SDK; reads credentials from `.env` via `python-dotenv`.
- **`database.py`** — SQLite-backed persistence layer with forward-compatible schema migration so existing `history.db` files are not broken when new columns are added.
- **`app.py`** — single-file Streamlit application structured around three tabs: Campaign Generator, Analytics, and History. CSV loading, feature engineering, and prompt construction all live here as pure functions.
- **`requirements.txt`** — minimal, pinned-floor dependencies covering only what the application actually imports.

---

## 3. Changes Made to `gemini.py`

Bob authored [`gemini.py`](gemini.py) from scratch:

- Configured an `OpenAI` client pointed at the OpenRouter base URL (`https://openrouter.ai/api/v1`) so the same `openai` SDK works with any OpenRouter-hosted model.
- API key is loaded from the `OPENROUTER_API_KEY` environment variable via `python-dotenv`; no credentials are hard-coded.
- `generate_email(prompt)` sends the prompt as a single `user` message to `openai/gpt-4o-mini` and returns the raw response text.
- The function raises a native exception on API failure, which is caught and displayed in the UI layer rather than silently swallowed here.

---

## 4. Changes Made to `database.py`

Bob authored [`database.py`](database.py) from scratch:

- `_get_connection()` — private helper that opens a connection to `history.db`.
- `init_db()` — creates the `history` table if it does not exist, then runs an additive migration (`PRAGMA table_info` + `ALTER TABLE ADD COLUMN`) to add `segment`, `subject`, and `generated_at` columns to any pre-existing database without data loss.
- `save_email(customer_id, income, spending, segment, subject, email)` — inserts a new history record with `datetime('now')` set by SQLite.
- `view_history()` — returns all rows ordered by `id DESC` (most recent first), selecting all eight columns for the History tab display.

---

## 5. Changes Made to `app.py`

Bob authored [`app.py`](app.py) from scratch. Key implementation decisions:

**CSV Loading (`load_csv`)**  
Reads the raw bytes and tries tab-separator first, then comma, before a final fallback — correctly handles the original dataset's tab-delimited format without requiring the user to pre-process the file.

**Feature Engineering (`enrich`)**  
Mirrors the notebook's segmentation logic exactly:
- `Age = 2026 − Year_Birth`
- `Total_Purchases = NumWebPurchases + NumCatalogPurchases + NumStorePurchases`
- `Total_Spent = MntWines + MntFruits + MntMeatProducts + MntFishProducts + MntSweetProducts + MntGoldProds`
- `Customer_Value = Total_Spent × Total_Purchases`
- `Segment`: Low (default) → Medium (≥ 5,000) → High (≥ 15,000)

**Prompt Construction (`build_prompt`)**  
Builds a structured, segmentation-aware prompt that includes: Education, Marital Status, Age, Annual Income, Total Spent, Total Purchases, Customer Value Score, Customer Segment, and Days Since Last Purchase. Three selectable tone modes (Professional, Friendly, Urgent) inject tone-specific instructions into the prompt.

**LLM Output Parsing (`parse_subject_body`)**  
Parses the model's `SUBJECT: / BODY:` formatted response into separate fields. Includes a graceful fallback that returns the full raw text as the body if the model does not follow the expected format.

**Session State Caching**  
The enriched DataFrame is stored in `st.session_state` keyed by filename so the CSV is only re-loaded and re-enriched when a different file is uploaded, not on every widget interaction.

---

## 6. `requirements.txt` Creation

Bob authored [`requirements.txt`](requirements.txt) with the minimum set of dependencies actually used by the application:

```
streamlit>=1.30.0
pandas>=2.0.0
openai>=1.0.0
python-dotenv>=1.0.0
```

No unused packages were added. Version floors were set to the minimum compatible releases rather than pinning exact versions, keeping the environment flexible for hackathon judges reproducing the project.

---

## 7. Segmentation Features

Bob implemented the full three-tier customer segmentation pipeline:

| Tier | Customer Value Threshold | UI Indicator |
|------|--------------------------|--------------|
| High | ≥ 15,000 | 🟢 |
| Medium | ≥ 5,000 | 🟡 |
| Low | < 5,000 | 🔴 |

The **Segment** column drives two behaviours:
1. **Campaign Generator tab** — a "Filter by Segment" selectbox lets the marketer narrow the customer list to a specific tier before selecting an individual customer.
2. **Prompt injection** — the segment label is passed directly into the AI prompt so the model tailors copy to each tier (e.g., premium offers for High, re-engagement for Low).

---

## 8. Analytics and UI Improvements

Bob implemented the **Analytics tab** (`tab_analytics` in [`app.py`](app.py:268)):

- **Segment Distribution** — bar chart of customer counts per tier, ordered High → Medium → Low.
- **Average Spending by Segment** — bar chart of mean `Total_Spent` per segment, same ordering.
- **Income Distribution** — income values binned into 10 equal-width buckets using `pd.cut`, rendered as a bar chart.
- **Dataset Summary** — `DataFrame.describe()` output scoped to the six computed columns (ID, Age, Income, Total_Spent, Total_Purchases, Customer_Value).

UI decisions made by Bob:
- Three-tab layout (Campaign Generator / Analytics / History) keeps concerns separated.
- Five-column metric row on the Customer Details card (`st.metric`) surfaces the most decision-relevant fields at a glance.
- Segment colour indicators (`SEGMENT_COLORS` dict) give instant visual context in the metric card.
- File uploader sits outside the tab group so it persists across tab switches.

---

## 9. Error Handling

Bob added defensive handling at every external boundary:

- **CSV loading** — tries tab and comma separators; falls back to pandas default on all errors; validates that an `ID` column exists before proceeding (`st.error` + `st.stop()`).
- **Missing columns** — all `enrich()` column derivations are guarded with `if col in df.columns` checks so the app works on partial datasets.
- **API failures** — the `generate_email` call is wrapped in a `try/except Exception` block that displays the exception message via `st.error` rather than crashing the app.
- **Empty segment filter** — if the selected segment yields zero customers, `st.warning` is shown and `st.stop()` prevents downstream key errors.
- **Missing Income values** — `fillna(0)` applied in `enrich()` prevents `f"${income:,.0f}"` format errors in the prompt and UI.
- **History tab with no data** — guarded by `if not history:` with an informational message.

---

## 10. Testing and Validation

Bob verified the application end-to-end against the provided dataset:

- Confirmed `load_csv` correctly reads `marketing_campaign.csv` (tab-separated, 2,240 rows, 29 columns).
- Verified all five derived columns (`Age`, `Total_Purchases`, `Total_Spent`, `Customer_Value`, `Segment`) are computed and present in the enriched DataFrame.
- Confirmed segment thresholds produce the expected three-tier distribution across the dataset.
- Verified `init_db()` runs without error on both a fresh database and an existing `history.db` with the old schema.
- Confirmed `save_email` and `view_history` round-trip data correctly (the History tab displays persisted records after generation).
- Confirmed `parse_subject_body` correctly splits the `SUBJECT:` / `BODY:` sections from representative LLM outputs.
- Verified the download buttons (`email_customer_{id}.txt` and `campaign_history.csv`) produce correctly formatted output.

---

## 11. Final Verification of the Working Streamlit Application

Bob performed a final check of the complete application:

- All imports resolve correctly with the packages listed in `requirements.txt`.
- `app.py` calls `init_db()` at module level before any Streamlit widget is rendered, ensuring the database is always ready.
- The three-tab layout renders without error when a valid CSV is uploaded.
- Email generation, history persistence, and CSV export all function end-to-end.
- The application handles the edge cases documented in §9 gracefully, with no unhandled exceptions surfacing to the user.

---

## IBM Bob Workflow Summary

```
Analysis
  └─ Examined main.ipynb, marketing_campaign.csv
  └─ Identified tab-separated CSV format, 29-column schema, notebook segmentation logic

Planning
  └─ Defined module responsibilities (gemini.py / database.py / app.py)
  └─ Designed forward-compatible DB schema and migration strategy

Implementation
  └─ Authored gemini.py  — OpenRouter LLM wrapper
  └─ Authored database.py — SQLite persistence with migration safety
  └─ Authored app.py     — full Streamlit UI, feature engineering, prompts, analytics
  └─ Authored requirements.txt — minimal dependency manifest

Testing
  └─ Validated CSV loading (tab + comma fallback)
  └─ Verified segmentation thresholds match notebook
  └─ Confirmed DB round-trip and LLM output parsing
  └─ Checked all error-handling branches

Documentation
  └─ Authored IBM_BOB_USAGE.md (this file)
```

---

*Generated by IBM Bob — AI Coding Assistant*
