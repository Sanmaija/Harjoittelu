from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "transactions.csv"

EXPENSE_CATEGORIES = [
    "Ruoka",
    "Juoma",
    "Ravintolat",
    "Asuminen",
    "Sähkö ja vesi",
    "Liikkuminen",
    "Autoilu",
    "Julkinen liikenne",
    "Vakuutukset",
    "Terveys ja apteekki",
    "Harrastukset",
    "Vapaa-aika",
    "Matkailu",
    "Vaatteet",
    "Elektroniikka",
    "Koti ja sisustus",
    "Lemmikit",
    "Lahjat",
    "Koulutus",
    "Sijoitukset",
    "Lainat",
    "Muut menot",
]


@dataclass
class Transaction:
    date: pd.Timestamp
    transaction_type: str
    category: str
    amount: float
    note: str



def ensure_data_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        pd.DataFrame(
            columns=["date", "type", "category", "amount", "note"]
        ).to_csv(DATA_FILE, index=False)



def load_data() -> pd.DataFrame:
    ensure_data_file()
    df = pd.read_csv(DATA_FILE)

    if df.empty:
        return pd.DataFrame(columns=["date", "type", "category", "amount", "note"])

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "amount", "type", "category"])
    return df



def save_transaction(transaction: Transaction) -> None:
    ensure_data_file()
    payload = pd.DataFrame(
        [
            {
                "date": transaction.date.date().isoformat(),
                "type": transaction.transaction_type,
                "category": transaction.category,
                "amount": transaction.amount,
                "note": transaction.note,
            }
        ]
    )
    payload.to_csv(DATA_FILE, mode="a", header=not DATA_FILE.stat().st_size, index=False)



def add_period_columns(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    working["day"] = working["date"].dt.strftime("%Y-%m-%d")
    working["week"] = (
        working["date"].dt.isocalendar().year.astype(str)
        + "-W"
        + working["date"].dt.isocalendar().week.astype(str).str.zfill(2)
    )
    working["month"] = working["date"].dt.strftime("%Y-%m")
    working["year"] = working["date"].dt.strftime("%Y")
    return working



def render_dashboard(df: pd.DataFrame) -> None:
    st.header("📊 Talouden yhteenveto")

    if df.empty:
        st.info("Ei vielä dataa. Lisää tapahtumia **Datan syöttö** -sivulla.")
        return

    df = add_period_columns(df)

    granularity = st.selectbox(
        "Valitse tarkastelutaso",
        options=[("day", "Päivä"), ("week", "Viikko"), ("month", "Kuukausi"), ("year", "Vuosi")],
        format_func=lambda item: item[1],
    )

    period_col = granularity[0]

    summary = (
        df.groupby([period_col, "type"], as_index=False)["amount"]
        .sum()
        .pivot(index=period_col, columns="type", values="amount")
        .fillna(0)
        .reset_index()
        .rename_axis(None, axis=1)
    )

    if "Tulot" not in summary.columns:
        summary["Tulot"] = 0
    if "Menot" not in summary.columns:
        summary["Menot"] = 0

    summary["Nettotulos"] = summary["Tulot"] - summary["Menot"]

    total_income = float(df.loc[df["type"] == "Tulot", "amount"].sum())
    total_expenses = float(df.loc[df["type"] == "Menot", "amount"].sum())
    net_result = total_income - total_expenses

    col1, col2, col3 = st.columns(3)
    col1.metric("Tulot yhteensä", f"{total_income:,.2f} €".replace(",", " "))
    col2.metric("Menot yhteensä", f"{total_expenses:,.2f} €".replace(",", " "))
    col3.metric("Nettotulos", f"{net_result:,.2f} €".replace(",", " "))

    bar_fig = px.bar(
        summary,
        x=period_col,
        y=["Tulot", "Menot", "Nettotulos"],
        barmode="group",
        title=f"Tulot, menot ja nettotulos ({granularity[1].lower()}tasolla)",
        labels={"value": "Euroa", period_col: "Jakso", "variable": "Tyyppi"},
    )
    st.plotly_chart(bar_fig, use_container_width=True)

    expense_df = df[df["type"] == "Menot"]
    if not expense_df.empty:
        pie_fig = px.pie(
            expense_df,
            names="category",
            values="amount",
            title="Menojen jakauma kategorioittain",
            hole=0.35,
        )
        st.plotly_chart(pie_fig, use_container_width=True)



def render_data_entry() -> None:
    st.header("➕ Lisää tulo tai meno")

    with st.form("transaction_form", clear_on_submit=True):
        date = st.date_input("Päivämäärä")
        transaction_type = st.radio("Tapahtuman tyyppi", options=["Tulot", "Menot"], horizontal=True)

        if transaction_type == "Tulot":
            category = "Tulot"
        else:
            category = st.selectbox("Menokategoria", EXPENSE_CATEGORIES)

        amount = st.number_input("Summa (€)", min_value=0.0, step=1.0)
        note = st.text_input("Lisätieto (valinnainen)")

        submitted = st.form_submit_button("Tallenna")

    if submitted:
        if amount <= 0:
            st.error("Summa pitää olla suurempi kuin 0 €.")
            return

        transaction = Transaction(
            date=pd.to_datetime(date),
            transaction_type=transaction_type,
            category=category,
            amount=float(amount),
            note=note.strip(),
        )
        save_transaction(transaction)
        st.success("Tapahtuma tallennettu!")

    st.divider()
    st.subheader("Viimeisimmät tapahtumat")
    df = load_data()
    if df.empty:
        st.write("Ei tapahtumia vielä.")
    else:
        latest = df.sort_values("date", ascending=False).head(15)
        st.dataframe(latest, use_container_width=True)



def main() -> None:
    st.set_page_config(page_title="Taloussuunnittelija", page_icon="💶", layout="wide")

    st.title("💶 Taloussuunnittelija")
    st.caption("Suunnittele omaa taloutta päivä-, viikko-, kuukausi- ja vuositasolla.")

    page = st.sidebar.radio("Sivu", ["Pääsivu", "Datan syöttö"])

    if page == "Pääsivu":
        render_dashboard(load_data())
    else:
        render_data_entry()


if __name__ == "__main__":
    main()
