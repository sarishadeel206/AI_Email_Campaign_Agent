import streamlit as st
import pandas as pd
import io

from gemini import generate_email
from database import init_db, save_email, view_history

# ── initialise DB once per process ────────────────────────────────────────────
init_db()

st.set_page_config(page_title="AI Email Campaign Agent", layout="wide")
st.title("AI Email Campaign Automation Agent")

# ══════════════════════════════════════════════════════════════════════════════
# helpers
# ══════════════════════════════════════════════════════════════════════════════

def load_csv(uploaded_file):
    """Read the uploaded CSV supporting both tab- and comma-separated files."""
    raw = uploaded_file.read()
    # try tab first (original dataset format), fall back to comma
    for sep in ("\t", ","):
        try:
            df = pd.read_csv(io.BytesIO(raw), sep=sep)
            if df.shape[1] > 1:          # more than one column means sep worked
                return df
        except Exception:
            continue
    return pd.read_csv(io.BytesIO(raw))  # last-resort default


def enrich(df):
    """
    Add computed columns that mirror the notebook's feature engineering:
      Age              = 2026 - Year_Birth
      Total_Purchases  = NumWebPurchases + NumCatalogPurchases + NumStorePurchases
      Total_Spent      = sum of the six Mnt* columns
      Customer_Value   = Total_Spent * Total_Purchases
      Segment          = Low / Medium / High  (thresholds from notebook)
    """
    cust = df.copy()

    # Age
    if "Year_Birth" in cust.columns:
        cust["Age"] = 2026 - cust["Year_Birth"]

    # Total purchases across channels
    purchase_cols = ["NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases"]
    if all(c in cust.columns for c in purchase_cols):
        cust["Total_Purchases"] = cust[purchase_cols].sum(axis=1)

    # Total amount spent across product categories
    spend_cols = [
        "MntWines", "MntFruits", "MntMeatProducts",
        "MntFishProducts", "MntSweetProducts", "MntGoldProds"
    ]
    if all(c in cust.columns for c in spend_cols):
        cust["Total_Spent"] = cust[spend_cols].sum(axis=1)

    # Customer value score
    if "Total_Spent" in cust.columns and "Total_Purchases" in cust.columns:
        cust["Customer_Value"] = cust["Total_Spent"] * cust["Total_Purchases"]

    # Segmentation thresholds (exact values from notebook cell 18)
    if "Customer_Value" in cust.columns:
        cust["Segment"] = "Low"
        cust.loc[cust["Customer_Value"] >= 5000, "Segment"] = "Medium"
        cust.loc[cust["Customer_Value"] >= 15000, "Segment"] = "High"

    # Fill missing Income with 0 for display / prompt safety
    if "Income" in cust.columns:
        cust["Income"] = cust["Income"].fillna(0)

    return cust


def build_prompt(row, tone):
    """Build an enriched, segmentation-aware AI prompt."""
    tone_instructions = {
        "Professional": "Write in a polished, formal, professional tone.",
        "Friendly":     "Write in a warm, conversational, friendly tone.",
        "Urgent":       "Write in an urgent, time-sensitive tone with a clear call to action.",
    }

    edu          = row.get("Education", "N/A")
    income       = row.get("Income", 0)
    marital      = row.get("Marital_Status", "N/A")
    age          = row.get("Age", "N/A")
    total_spent  = row.get("Total_Spent", "N/A")
    total_purch  = row.get("Total_Purchases", "N/A")
    cust_value   = row.get("Customer_Value", "N/A")
    segment      = row.get("Segment", "N/A")
    recency      = row.get("Recency", "N/A")

    prompt = f"""You are a marketing copywriter. Generate a personalized marketing email for a customer.

Return your response in exactly this format (two clearly labelled sections):
SUBJECT: <one-line email subject>
BODY:
<email body — under 150 words>

Customer Profile:
- Education: {edu}
- Marital Status: {marital}
- Age: {age}
- Annual Income: ${income:,.0f}
- Total Spent: ${total_spent}
- Total Purchases: {total_purch}
- Customer Value Score: {cust_value}
- Customer Segment: {segment}  (Low / Medium / High)
- Days Since Last Purchase: {recency}

Tone instruction: {tone_instructions[tone]}

Tailor the email to match the customer's segment and profile. Do not include placeholders like [Name] or [Company].
"""
    return prompt


def parse_subject_body(raw_text):
    """
    Parse the LLM output into (subject, body).
    Expected format:
        SUBJECT: <subject line>
        BODY:
        <body>
    Falls back gracefully if the model doesn't follow the format.
    """
    subject = ""
    body = raw_text.strip()

    lines = raw_text.strip().splitlines()
    body_lines = []
    in_body = False

    for line in lines:
        if line.upper().startswith("SUBJECT:"):
            subject = line.split(":", 1)[1].strip()
        elif line.upper().startswith("BODY:"):
            in_body = True
        elif in_body:
            body_lines.append(line)

    if body_lines:
        body = "\n".join(body_lines).strip()

    return subject, body


SEGMENT_COLORS = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}

# ══════════════════════════════════════════════════════════════════════════════
# file upload (outside tabs — persists across tab switches)
# ══════════════════════════════════════════════════════════════════════════════

file = st.file_uploader("Upload Customer CSV", type="csv")

if not file:
    st.info("Upload a customer CSV file to get started.")
    st.stop()

# load + enrich once, cache in session state
if "data" not in st.session_state or st.session_state.get("file_name") != file.name:
    st.session_state["data"] = enrich(load_csv(file))
    st.session_state["file_name"] = file.name

data = st.session_state["data"]

if "ID" not in data.columns:
    st.error("The uploaded CSV does not contain an 'ID' column. Please check the file format.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# tabs
# ══════════════════════════════════════════════════════════════════════════════

tab_campaign, tab_analytics, tab_history = st.tabs(
    ["📧 Campaign Generator", "📊 Analytics", "🕓 History"]
)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Campaign Generator
# ─────────────────────────────────────────────────────────────────────────────
with tab_campaign:

    st.subheader("Customer Data Preview")
    st.dataframe(data.head(10), use_container_width=True)

    # Segment filter
    segments = ["All"] + sorted(data["Segment"].unique().tolist()) if "Segment" in data.columns else ["All"]
    selected_segment = st.selectbox("Filter by Segment", segments)

    if selected_segment != "All":
        filtered = data[data["Segment"] == selected_segment]
    else:
        filtered = data

    if filtered.empty:
        st.warning("No customers match this segment filter.")
        st.stop()

    ids = filtered["ID"].tolist()
    cid = st.selectbox("Select Customer ID", ids)

    row_df = filtered[filtered["ID"] == cid]
    row = row_df.iloc[0].to_dict()

    # Customer detail card
    st.subheader("Customer Details")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Customer ID", cid)
    col2.metric("Income", f"${row.get('Income', 0):,.0f}")
    col3.metric("Total Spent", f"${row.get('Total_Spent', 'N/A')}")
    col4.metric("Total Purchases", row.get("Total_Purchases", "N/A"))

    segment_val = row.get("Segment", "N/A")
    col5.metric("Segment", f"{SEGMENT_COLORS.get(segment_val, '')} {segment_val}")

    st.dataframe(row_df, use_container_width=True)

    st.markdown("---")

    # Tone selector
    tone = st.radio(
        "Email Tone",
        ["Professional", "Friendly", "Urgent"],
        horizontal=True
    )

    if st.button("✉️ Generate Email", type="primary"):
        prompt = build_prompt(row, tone)

        with st.spinner("Generating personalised email…"):
            try:
                raw = generate_email(prompt)
                subject, body = parse_subject_body(raw)

                save_email(
                    customer_id=cid,
                    income=row.get("Income", 0),
                    spending=row.get("Total_Spent", 0),
                    segment=segment_val,
                    subject=subject,
                    email=body,
                )

                st.success("Email generated successfully!")

                st.subheader("📨 Generated Email")
                if subject:
                    st.markdown(f"**Subject:** {subject}")
                st.text_area("Email Body", body, height=250)

                full_email = f"Subject: {subject}\n\n{body}" if subject else body
                st.download_button(
                    label="⬇ Download Email",
                    data=full_email,
                    file_name=f"email_customer_{cid}.txt",
                    mime="text/plain",
                )

            except Exception as exc:
                st.error(f"Email generation failed: {exc}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Analytics
# ─────────────────────────────────────────────────────────────────────────────
with tab_analytics:
    st.subheader("Customer Analytics")

    if "Segment" not in data.columns:
        st.info("Segment data not available — ensure the uploaded CSV contains the required columns.")
    else:
        col_a, col_b = st.columns(2)

        # Segment distribution
        with col_a:
            st.markdown("**Segment Distribution**")
            seg_counts = (
                data["Segment"]
                .value_counts()
                .reindex(["High", "Medium", "Low"])
                .dropna()
                .reset_index()
            )
            seg_counts.columns = ["Segment", "Count"]
            st.bar_chart(seg_counts.set_index("Segment"))

        # Average spending by segment
        with col_b:
            st.markdown("**Average Spending by Segment**")
            if "Total_Spent" in data.columns:
                avg_spend = (
                    data.groupby("Segment")["Total_Spent"]
                    .mean()
                    .reindex(["High", "Medium", "Low"])
                    .dropna()
                    .round(2)
                    .reset_index()
                )
                avg_spend.columns = ["Segment", "Avg_Spent"]
                st.bar_chart(avg_spend.set_index("Segment"))
            else:
                st.info("Total_Spent column not available.")

        # Income distribution
        st.markdown("**Income Distribution**")
        if "Income" in data.columns:
            income_data = data["Income"].dropna()
            # bin into 10 equal-width buckets and count
            income_hist = (
                pd.cut(income_data, bins=10)
                .value_counts()
                .sort_index()
                .reset_index()
            )
            income_hist.columns = ["Income Range", "Count"]
            income_hist["Income Range"] = income_hist["Income Range"].astype(str)
            st.bar_chart(income_hist.set_index("Income Range"))
        else:
            st.info("Income column not available.")

        # Summary statistics
        st.markdown("**Dataset Summary**")
        summary_cols = [c for c in ["ID", "Age", "Income", "Total_Spent", "Total_Purchases", "Customer_Value"] if c in data.columns]
        st.dataframe(data[summary_cols].describe().round(2), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — History
# ─────────────────────────────────────────────────────────────────────────────
with tab_history:
    st.subheader("Campaign History")

    history = view_history()

    if not history:
        st.info("No emails have been generated yet.")
    else:
        history_df = pd.DataFrame(
            history,
            columns=["ID", "Customer ID", "Income", "Total Spending", "Segment", "Subject", "Email Body", "Generated At"]
        )
        st.dataframe(history_df, use_container_width=True)

        csv_export = history_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ Export History as CSV",
            data=csv_export,
            file_name="campaign_history.csv",
            mime="text/csv",
        )

st.markdown("---")
st.caption("AI Email Campaign Automation Agent")
