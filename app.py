import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

from engine.market_engine import run_market_simulation
from ui.style import setup_page

DATA_DIR = Path("data")
COMPANIES_FILE = DATA_DIR / "companies.csv"
DECISIONS_FILE = DATA_DIR / "decisions.csv"
RESULTS_FILE = DATA_DIR / "results.csv"
ANNOUNCEMENTS_FILE = DATA_DIR / "announcements.csv"

# ---- CONFIG ----
GAME_MASTER_CODE = "MASTER-2025"   # 👉 change this before the semester


# ---------- HELPERS ----------
def load_csv(path: Path, columns=None) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    elif columns:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame()

def save_csv(df: pd.DataFrame, path: Path):
    df.to_csv(path, index=False)

def get_current_week() -> int:
    return st.session_state.get("current_week", 1)

def set_current_week(week: int):
    st.session_state["current_week"] = int(week)


# ---------- AUTH / LOGIN ----------
def login_page(companies_df: pd.DataFrame):
    st.markdown("### Login")

    role = st.radio("I am a:", ["BA Team", "BI Team", "Instructor (Game Master)"])

    if role == "Instructor (Game Master)":
        code = st.text_input("Game Master code", type="password")
        if st.button("Login as Instructor"):
            if code == GAME_MASTER_CODE:
                st.session_state["logged_in"] = True
                st.session_state["role"] = "INSTRUCTOR"
                st.session_state["company_id"] = None
                st.success("Logged in as Instructor.")
            else:
                st.error("Incorrect Game Master code.")
        return

    # BA / BI login
    company_id = st.selectbox("Company", companies_df["company_id"])
    col1, col2 = st.columns(2)
    with col1:
        code = st.text_input("Team login code", type="password")
    with col2:
        phone = st.text_input("Team contact phone (optional)")

    if st.button("Login"):
        row = companies_df[companies_df["company_id"] == company_id].iloc[0]
        if role == "BA Team":
            expected = row["ba_code"]
        else:
            expected = row["bi_code"]

        if str(code).strip() == str(expected):
            st.session_state["logged_in"] = True
            st.session_state["role"] = "BA" if role == "BA Team" else "BI"
            st.session_state["company_id"] = int(company_id)
            st.session_state["company_name"] = row["company_name"]
            st.session_state["team_phone"] = phone
            st.success(f"Logged in as {role} for {row['company_name']}.")
        else:
            st.error("Invalid code for this company.")


# ---------- PAGES ----------
def page_home():
    role = st.session_state.get("role")
    company_name = st.session_state.get("company_name", "–")
    week = get_current_week()

    st.title("Business Strategy Simulation")
    st.write(f"**Current week:** {week}")

    if role in ["BA", "BI"]:
        st.info(f"You are logged in as **{role} team** for **{company_name}**.")
    elif role == "INSTRUCTOR":
        st.info("You are logged in as **Instructor (Game Master)**.")
    else:
        st.warning("Please log in from the sidebar to access features.")


def page_announcements():
    st.header("Weekly Announcements")
    week = get_current_week()
    announcements = load_csv(ANNOUNCEMENTS_FILE, ["week", "title", "body"])

    current = announcements[announcements["week"] == week]
    if not current.empty:
        row = current.iloc[0]
        st.subheader(f"Week {int(row['week'])}: {row['title']}")
        st.write(row["body"])
    else:
        st.info("No announcement for this week yet.")

    with st.expander("All announcements"):
        st.dataframe(announcements.sort_values("week"))


def page_ba_team(companies_df: pd.DataFrame):
    if st.session_state.get("role") != "BA":
        st.warning("This page is for BA Teams only.")
        return

    company_id = st.session_state["company_id"]
    company_name = st.session_state["company_name"]
    week = get_current_week()

    st.header(f"BA Decisions – {company_name} (Week {week})")

    decisions = load_csv(
        DECISIONS_FILE,
        ["week","company_id","role","price","quantity","marketing",
         "forecast_demand","notes","phone_number","timestamp"]
    )

    price = st.number_input("Price", min_value=1.0, value=100.0, step=1.0)
    quantity = st.number_input("Production quantity", min_value=0, value=20000, step=100)
    marketing = st.number_input("Marketing intensity (0–10)", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
    notes = st.text_area("Notes / rationale (optional)")
    phone = st.session_state.get("team_phone", "")

    if st.button("Submit BA decision"):
        new_row = {
            "week": week,
            "company_id": company_id,
            "role": "BA",
            "price": price,
            "quantity": quantity,
            "marketing": marketing,
            "forecast_demand": np.nan,
            "notes": notes,
            "phone_number": phone,
            "timestamp": datetime.now().isoformat(),
        }
        decisions = pd.concat([decisions, pd.DataFrame([new_row])], ignore_index=True)
        save_csv(decisions, DECISIONS_FILE)
        st.success("Decision submitted.")

    st.markdown("---")
    st.subheader("History – BA & BI for your company")
    company_decisions = decisions[decisions["company_id"] == company_id].sort_values(["week","role"])
    st.dataframe(company_decisions)


def page_bi_team(companies_df: pd.DataFrame):
    if st.session_state.get("role") != "BI":
        st.warning("This page is for BI Teams only.")
        return

    company_id = st.session_state["company_id"]
    company_name = st.session_state["company_name"]
    week = get_current_week()

    st.header(f"BI Forecasts & Analytics – {company_name} (Week {week})")

    decisions = load_csv(
        DECISIONS_FILE,
        ["week","company_id","role","price","quantity","marketing",
         "forecast_demand","notes","phone_number","timestamp"]
    )

    forecast = st.number_input("Forecast demand for this week", min_value=0, value=20000, step=100)
    notes = st.text_area("Explain your model / assumptions (optional)")
    phone = st.session_state.get("team_phone", "")

    if st.button("Submit BI forecast"):
        new_row = {
            "week": week,
            "company_id": company_id,
            "role": "BI",
            "price": np.nan,
            "quantity": np.nan,
            "marketing": np.nan,
            "forecast_demand": forecast,
            "notes": notes,
            "phone_number": phone,
            "timestamp": datetime.now().isoformat(),
        }
        decisions = pd.concat([decisions, pd.DataFrame([new_row])], ignore_index=True)
        save_csv(decisions, DECISIONS_FILE)
        st.success("Forecast submitted.")

    st.markdown("---")
    st.subheader("History – BA & BI for your company")
    company_decisions = decisions[decisions["company_id"] == company_id].sort_values(["week","role"])
    st.dataframe(company_decisions)


def page_leaderboard():
    st.header("Leaderboard")
    results = load_csv(RESULTS_FILE, ["week","company_id","company_name",
                                      "price","quantity","marketing","market_share",
                                      "demand","sold_qty","revenue","total_cost","profit","score"])
    if results.empty:
        st.info("No results yet.")
        return

    min_w = int(results["week"].min())
    max_w = int(results["week"].max())
    week = st.slider("Select week", min_w, max_w, max_w)

    df = results[results["week"] == week]
    leaderboard = (
        df.groupby(["company_id","company_name"])["score"]
        .sum()
        .reset_index()
        .sort_values("score", ascending=False)
    )
    leaderboard["rank"] = range(1, len(leaderboard)+1)
    st.dataframe(leaderboard[["rank","company_id","company_name","score"]])


def page_instructor(companies_df: pd.DataFrame):
    if st.session_state.get("role") != "INSTRUCTOR":
        st.warning("Instructor access only.")
        return

    st.header("Instructor Panel")

    # Week control
    st.subheader("Week control")
    current_week = get_current_week()
    new_week = st.number_input("Current week", min_value=1, value=current_week, step=1)
    if st.button("Update week"):
        set_current_week(new_week)
        st.success(f"Week set to {new_week}")

    # Announcements
    st.markdown("---")
    st.subheader("Announcements")
    announcements = load_csv(ANNOUNCEMENTS_FILE, ["week","title","body"])

    with st.form("announcement_form"):
        aw = st.number_input("Week", min_value=1, value=get_current_week(), step=1)
        title = st.text_input("Title")
        body = st.text_area("Body")
        submitted = st.form_submit_button("Save announcement")
        if submitted:
            announcements = announcements[announcements["week"] != aw]
            announcements = pd.concat(
                [announcements, pd.DataFrame([{"week": int(aw), "title": title, "body": body}])],
                ignore_index=True,
            )
            save_csv(announcements, ANNOUNCEMENTS_FILE)
            st.success("Announcement saved.")

    # Simulation
    st.markdown("---")
    st.subheader("Run simulation")
    decisions = load_csv(
        DECISIONS_FILE,
        ["week","company_id","role","price","quantity","marketing",
         "forecast_demand","notes","phone_number","timestamp"]
    )
    results = load_csv(
        RESULTS_FILE,
        ["week","company_id","company_name","price","quantity","marketing",
         "market_share","demand","sold_qty","revenue","total_cost","profit","score"]
    )
    week = get_current_week()
    st.write(f"BA decisions for week {week}:",
             len(decisions[(decisions['week'] == week) & (decisions['role'] == 'BA')]))

    if st.button("Run simulation for current week"):
        week_results = run_market_simulation(week, companies_df, decisions)
        if week_results.empty:
            st.warning("No BA decisions for this week.")
        else:
            results = results[results["week"] != week]
            results = pd.concat([results, week_results], ignore_index=True)
            save_csv(results, RESULTS_FILE)
            st.success("Simulation completed.")
            st.dataframe(week_results)

    st.markdown("---")
    st.subheader("Raw data")
    with st.expander("Decisions"):
        st.dataframe(decisions.sort_values(["week","company_id","role"]))
    with st.expander("Results"):
        st.dataframe(results.sort_values(["week","company_id"]))


# ---------- MAIN ----------
def main():
    setup_page()

    companies_df = load_csv(COMPANIES_FILE)

    # Sidebar: login & navigation
    st.sidebar.title("Simulation Portal")

    if not st.session_state.get("logged_in"):
        login_page(companies_df)
        st.sidebar.info("Log in to access pages.")
        return

    role = st.session_state.get("role")
    page = st.sidebar.radio(
        "Go to",
        ["Home","Announcements"] +
        (["BA – Decisions"] if role == "BA" else []) +
        (["BI – Analytics"] if role == "BI" else []) +
        ["Leaderboard"] +
        (["Instructor Panel"] if role == "INSTRUCTOR" else [])
    )

    if page == "Home":
        page_home()
    elif page == "Announcements":
        page_announcements()
    elif page == "BA – Decisions":
        page_ba_team(companies_df)
    elif page == "BI – Analytics":
        page_bi_team(companies_df)
    elif page == "Leaderboard":
        page_leaderboard()
    elif page == "Instructor Panel":
        page_instructor(companies_df)

if __name__ == "__main__":
    main()
