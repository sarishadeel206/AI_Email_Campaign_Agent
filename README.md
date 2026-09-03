# AI Email Campaign Automation Agent

An intelligent, data-driven marketing tool that reads a customer dataset, segments customers by behavioural value, and generates personalised marketing emails using a large language model — all through a clean Streamlit web interface.

---

## Problem Statement

Marketing teams working with large customer databases face two compounding challenges:

1. **Scale** — Writing individual, personalised emails for thousands of customers is not feasible manually.
2. **Relevance** — Generic bulk emails produce low engagement because they ignore each customer's actual spending behaviour, purchase history, and income profile.

Existing automation tools either send identical copy to every recipient or require expensive CRM integrations. There is a gap for a lightweight, open-source tool that combines customer segmentation with LLM-powered copy generation.

---

## Solution

The AI Email Campaign Automation Agent solves both problems in a single workflow:

- It **segments** customers automatically into High / Medium / Low value tiers based on their purchase history and total spending.
- It **generates** a personalised email for each customer using a contextual prompt that injects that customer's profile and segment into a large language model.
- It **persists** every generated email in a local SQLite database so campaign history is never lost.
- It **surfaces** analytics — segment distribution, spending patterns, income distribution — so marketers can understand their audience before generating campaigns.

No CRM, no cloud database, no complex setup required. Upload a CSV and get personalised emails in seconds.

---

## Key Features

| Feature | Detail |
|---|---|
| **Three-tier customer segmentation** | Low / Medium / High tiers driven by a `Customer_Value` score (spent × purchases) |
| **AI email generation** | GPT-4o-mini via OpenRouter; returns a formatted subject line + body |
| **Three selectable tones** | Professional, Friendly, Urgent — injected into the LLM prompt |
| **Segment-aware filtering** | Filter the customer list to a specific tier before generating |
| **Customer detail card** | Five-column metric view (ID, Income, Total Spent, Total Purchases, Segment) |
| **Campaign history** | Every generated email saved to SQLite with timestamp |
| **CSV export** | Download the full history as `campaign_history.csv` |
| **Per-email download** | Download any generated email as `email_customer_{id}.txt` |
| **Analytics dashboard** | Segment distribution, average spending by segment, income histogram, dataset summary |
| **Robust CSV loading** | Tries tab-separator first, then comma — handles the original dataset format automatically |
| **Forward-compatible DB schema** | Additive migrations ensure existing databases are never broken on upgrade |

---

## Application Workflow

```
Upload CSV
    │
    ▼
Load & Enrich DataFrame
    │  Age = 2026 - Year_Birth
    │  Total_Purchases = Web + Catalog + Store purchases
    │  Total_Spent     = sum of all Mnt* spend columns
    │  Customer_Value  = Total_Spent × Total_Purchases
    │  Segment         = Low (<5,000) / Medium (≥5,000) / High (≥15,000)
    │
    ├──▶  Campaign Generator tab
    │         Select segment filter → select customer → choose tone
    │         → Build prompt → Call LLM via OpenRouter
    │         → Parse SUBJECT / BODY → Save to SQLite → Display + Download
    │
    ├──▶  Analytics tab
    │         Segment distribution bar chart
    │         Average spending by segment bar chart
    │         Income distribution histogram
    │         Dataset summary statistics
    │
    └──▶  History tab
              Display all saved emails (most recent first)
              Export full history as CSV
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| **UI framework** | [Streamlit](https://streamlit.io/) ≥ 1.30 |
| **Data processing** | [pandas](https://pandas.pydata.org/) ≥ 2.0 |
| **LLM API client** | [openai](https://pypi.org/project/openai/) ≥ 1.0 (OpenAI-compatible SDK) |
| **LLM routing** | [OpenRouter](https://openrouter.ai/) — `openai/gpt-4o-mini` |
| **Persistence** | SQLite via Python `sqlite3` (standard library) |
| **Environment config** | [python-dotenv](https://pypi.org/project/python-dotenv/) ≥ 1.0 |
| **AI coding assistant** | [IBM Bob](https://www.ibm.com/products/bob) |

---

## Project Structure

```
AI EMAIL AGENT/
├── app.py                  # Streamlit application — UI, feature engineering, prompt logic
├── gemini.py               # OpenRouter LLM wrapper (OpenAI-compatible client)
├── database.py             # SQLite persistence — init, save, view history
├── requirements.txt        # Minimal runtime dependencies
├── marketing_campaign.csv  # Sample customer dataset (2,240 rows, 29 columns)
├── history.db              # SQLite database (auto-created on first run)
├── main.ipynb              # Exploratory notebook — segmentation logic and thresholds
├── IBM_BOB_USAGE.md        # IBM Bob AI assistant contribution log
└── IBM Bob/                # IBM Bob desktop application (local install)
```

---

## Installation and Setup

### Prerequisites

- Python 3.9 or higher
- An [OpenRouter](https://openrouter.ai/) account and API key

### 1. Clone the repository

```bash
git clone <repository-url>
cd "AI EMAIL AGENT"
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` contains:

```
streamlit>=1.30.0
pandas>=2.0.0
openai>=1.0.0
python-dotenv>=1.0.0
```

### 4. Configure the OpenRouter API key

Create a `.env` file in the project root:

```bash
# .env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

> **How to get an API key:**  
> 1. Sign up at [openrouter.ai](https://openrouter.ai/)  
> 2. Go to **Keys** in your dashboard  
> 3. Click **Create Key** and copy the value  
> 4. Paste it into the `.env` file above  

The `.env` file is listed in `.gitignore` — your key will never be committed to version control.

---

## Running the Application

```bash
streamlit run app.py
```

Streamlit will open the application at `http://localhost:8501` in your default browser.

### Using the application

1. **Upload a CSV** — use `marketing_campaign.csv` (included) or any compatible customer dataset. The file uploader accepts both tab-separated and comma-separated files.

2. **Campaign Generator tab**
   - Optionally filter by segment (All / High / Medium / Low)
   - Select a customer ID from the dropdown
   - Review the customer detail card (Income, Total Spent, Total Purchases, Segment tier)
   - Choose an email tone: **Professional**, **Friendly**, or **Urgent**
   - Click **✉️ Generate Email**
   - Copy the subject and body, or use **⬇ Download Email** to save as a `.txt` file

3. **Analytics tab** — view segment distribution, average spending per tier, income histogram, and descriptive statistics for the dataset

4. **History tab** — browse every previously generated email with timestamps; export the full log as `campaign_history.csv`

---

## Dataset Format

The included `marketing_campaign.csv` is a tab-separated file with 2,240 customer rows and 29 columns. Key columns used by the application:

| Column | Used for |
|---|---|
| `ID` | Customer identifier |
| `Year_Birth` | Derives `Age` |
| `Education` | Prompt context |
| `Marital_Status` | Prompt context |
| `Income` | Prompt context, metric card |
| `MntWines`, `MntFruits`, `MntMeatProducts`, `MntFishProducts`, `MntSweetProducts`, `MntGoldProds` | Derives `Total_Spent` |
| `NumWebPurchases`, `NumCatalogPurchases`, `NumStorePurchases` | Derives `Total_Purchases` |
| `Recency` | Days since last purchase — used in prompt |

---

## Customer Segmentation Logic

Segmentation mirrors the thresholds established in `main.ipynb`:

```
Customer_Value = Total_Spent × Total_Purchases

Segment = "High"    if Customer_Value ≥ 15,000   🟢
Segment = "Medium"  if Customer_Value ≥  5,000   🟡
Segment = "Low"     if Customer_Value <  5,000   🔴
```

The segment label is passed directly into the LLM prompt so the model tailors its copy accordingly — premium retention messaging for High, re-engagement offers for Low.

---

## IBM Bob Usage

IBM Bob (Agent Mode) was used as the primary AI coding assistant throughout this project. Bob performed:

- **Analysis** — examined `main.ipynb` and `marketing_campaign.csv` to extract segmentation logic and dataset structure
- **Planning** — designed the three-module architecture (`gemini.py`, `database.py`, `app.py`) and the forward-compatible DB schema strategy
- **Implementation** — authored all three Python source files and `requirements.txt` from scratch
- **Testing** — validated CSV loading, segmentation thresholds, DB round-trip, LLM output parsing, and all error-handling branches
- **Documentation** — produced `IBM_BOB_USAGE.md` with a full contribution log

Full details are in [`IBM_BOB_USAGE.md`](IBM_BOB_USAGE.md).

---

## Testing and Validation

The application was validated end-to-end against the provided dataset:

- `load_csv` correctly reads `marketing_campaign.csv` (tab-separated, 2,240 rows, 29 columns)
- All five derived columns (`Age`, `Total_Purchases`, `Total_Spent`, `Customer_Value`, `Segment`) are computed correctly
- Segmentation thresholds produce the expected three-tier distribution across the full dataset
- `init_db()` runs without error on both a fresh database and a pre-existing `history.db`
- `save_email` and `view_history` correctly round-trip data through SQLite
- `parse_subject_body` correctly splits `SUBJECT:` / `BODY:` sections from representative LLM outputs
- Download buttons produce correctly formatted `.txt` and `.csv` output
- All error-handling branches (empty segment, missing columns, API failure, no history) behave gracefully

---

## Future Scope

- **Batch generation** — generate emails for an entire segment or the full dataset in one run, with progress tracking
- **Email template library** — save and reuse prompt templates for recurring campaign types
- **A/B subject line variants** — ask the LLM to produce two subject line options per email for split testing
- **Multi-model support** — expose a model selector in the UI so users can switch between GPT-4o-mini, Claude, Mistral, and other OpenRouter-hosted models
- **Scheduled campaigns** — integrate a scheduler (APScheduler or a cron job) to trigger generation and delivery at a set time
- **Email delivery integration** — connect to SendGrid, Mailgun, or AWS SES to send generated emails directly from the UI
- **Authentication** — add a simple login layer before deploying to a shared or cloud environment
- **Cloud deployment** — Dockerise the application and deploy to Streamlit Community Cloud, AWS, or GCP for team-wide access

---

## License

This project was developed as a hackathon submission. See repository for license details.
