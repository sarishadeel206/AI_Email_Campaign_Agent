import streamlit as st
import pandas as pd

from gemini import generate_email
from database import save_email, view_history

st.set_page_config(page_title="AI Email Campaign Agent", layout="wide")

st.title("AI Email Campaign Automation Agent")

file = st.file_uploader("Upload Customer CSV", type="csv")

if file:

    data = pd.read_csv(file, sep="\t")

    st.subheader("Customer Data")
    st.dataframe(data.head(10))

    ids = data["ID"].tolist()

    cid = st.selectbox("Select Customer ID", ids)

    row = data[data["ID"] == cid]

    st.subheader("Customer Details")
    st.dataframe(row)

    edu = row["Education"].values[0]
    income = row["Income"].values[0]

    spent = (
        row["MntWines"].values[0]
        + row["MntFruits"].values[0]
        + row["MntMeatProducts"].values[0]
        + row["MntFishProducts"].values[0]
        + row["MntSweetProducts"].values[0]
        + row["MntGoldProds"].values[0]
    )

    prompt = f"""
Write a professional personalized marketing email.

Customer Education: {edu}
Customer Income: {income}
Total Spending: {spent}

Write a friendly marketing email in less than 150 words.
"""

    if st.button("Generate Email"):

        mail = generate_email(prompt)

        save_email(cid, income, spent, mail)

        st.subheader("Generated Email")
        st.write(mail)

        st.download_button(
            "Download Email",
            mail,
            file_name="marketing_email.txt"
        )

        st.success("Email Generated Successfully")

    st.markdown("---")

    st.metric("Customer ID", cid)
    st.metric("Income", income)
    st.metric("Total Spending", spent)

    st.markdown("---")

    if st.button("View History"):

        history = view_history()

        history = pd.DataFrame(
            history,
            columns=[
                "ID",
                "Customer ID",
                "Income",
                "Total Spending",
                "Email"
            ]
        )

        st.subheader("Campaign History")
        st.dataframe(history)

    st.markdown("---")
    st.caption("AI Email Campaign Automation Agent")