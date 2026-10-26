<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:172554,50:0F766E,100:14B8A6&height=190&section=header&text=AI%20Email%20Campaign%20Agent&fontSize=32&fontColor=FFFFFF&fontAlignY=40&desc=Customer%20Insights%20%7C%20Personalized%20Messaging%20%7C%20Generative%20AI&descSize=12&descAlignY=64" width="100%" alt="AI Email Campaign Agent header"/>

# AI Email Campaign Automation Agent

### From Customer Behaviour to Context-Aware Email Drafts

**Developed by Sarish Adeel**

<br>

<img src="https://img.shields.io/badge/Python-2563EB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/Streamlit-0F766E?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
<img src="https://img.shields.io/badge/Pandas-7C3AED?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas"/>
<img src="https://img.shields.io/badge/OpenRouter-1E293B?style=for-the-badge" alt="OpenRouter"/>
<img src="https://img.shields.io/badge/SQLite-0E7490?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
<img src="https://img.shields.io/badge/IBM%20Bob-AI%20Assistant-475569?style=for-the-badge&logo=ibm&logoColor=white" alt="IBM Bob"/>

<br><br>

[Repository](https://github.com/sarishadeel206/AI_Email_Campaign_Agent) · [OpenRouter](https://openrouter.ai/) · [Streamlit](https://streamlit.io/)

</div>

---

## Overview

Personalized marketing takes more than sending the same message to every customer. This application combines customer-level analytics with a large language model to prepare relevant email drafts from a customer dataset.

With a Streamlit interface, users can explore customer value segments, choose a customer and writing tone, generate an email draft, download the result, and revisit previous drafts.

> **Scope:** The application generates and stores drafts for review. It does not automatically send emails.

## At a Glance

| Capability | Description |
|---|---|
| Customer analysis | Derives purchase and spending metrics from customer records |
| Value-based segmentation | Classifies customers as Low, Medium, or High value |
| AI-written drafts | Generates a subject line and email body using customer context |
| Tone controls | Professional, Friendly, or Urgent |
| Campaign history | Stores generated messages in SQLite |
| Analytics dashboard | Summarizes segments, spending, and income |
| Export | Downloads individual drafts and campaign history |

## Workflow

<div align="center">

<img src="https://raw.githubusercontent.com/sarishadeel206/AI_Email_Campaign_Agent/main/project_workflow.png" width="100%" alt="AI Email Campaign Agent workflow"/>

</div>

**Upload dataset → Prepare customer metrics → Segment customers → Build a contextual prompt → Generate a draft → Review, download, and save history**

## Customer Metrics

The application derives its customer measures from the dataset:

| Measure | Definition |
|---|---|
| Total Purchases | Web + catalog + store purchases |
| Total Spent | Sum of the product spending columns |
| Customer Value | Total Spent × Total Purchases |

### Segment thresholds

- 🟢 **High:** Customer Value ≥ 15,000
- 🟡 **Medium:** Customer Value ≥ 5,000 and < 15,000
- 🔴 **Low:** Customer Value < 5,000

These are the thresholds used by the project’s segmentation logic.

## Technology

| Component | Purpose |
|---|---|
| Python | Application logic and calculations |
| Pandas | Data loading and processing |
| Streamlit | Interactive web interface |
| OpenRouter API | Routes requests to the configured language model |
| OpenAI-compatible SDK | Communicates with the model API |
| SQLite | Stores campaign history |
| python-dotenv | Loads the API key from environment configuration |
| IBM Bob | AI-assisted coding support |

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/sarishadeel206/AI_Email_Campaign_Agent.git
cd AI_Email_Campaign_Agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API key

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Add your own OpenRouter API key in place of the placeholder.

### 4. Launch the app

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open it in your browser to use the app.

> **Security reminder:** Never commit your `.env` file, API keys, or private customer data to the repository.

## Using the App

1. Load the included customer dataset or another compatible CSV/TSV file.
2. Open the campaign generator and optionally filter by customer segment.
3. Select a customer and choose an email tone.
4. Generate the email draft and review its subject and body.
5. Download the draft or check the saved records under campaign history.
6. Use the analytics view to explore segment distribution and spending patterns.

## Dataset

The included `marketing_campaign.csv` contains **2,240 customer records and 29 columns**. The application uses purchase history, spending measures, income, and other customer attributes to prepare the metrics and contextual information used for draft generation.

## AI-Assisted Development

IBM Bob was used as an AI coding assistant during project analysis, implementation, testing, and documentation. The application itself uses the OpenRouter API to request generated email content.

## Future Improvements

- Batch draft generation for selected customer segments
- A/B subject-line variants and reusable templates
- Campaign scheduling and email delivery integration
- Authentication and cloud deployment
- Additional campaign performance tracking

---

<div align="center">

### Customer Analytics • Generative AI • Personalized Communication

**AI Email Campaign Automation Agent**  
<sub>Built by Sarish Adeel with Python, Streamlit, and OpenRouter.</sub>

</div>
