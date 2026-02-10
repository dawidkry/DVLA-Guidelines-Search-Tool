import streamlit as st
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Tool", page_icon="🩺", layout="wide")

# This is your "Database". You'll need to check this against GOV.UK once a year.
DVLA_GUIDELINES = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {"g1": "1 month off.", "g2": "1 year off.", "g1_m": 1, "g2_m": 12},
            "First Seizure": {"g1": "6-12 months off.", "g2": "5 years off.", "g1_m": 6, "g2_m": 60}
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI (STEMI/NSTEMI)": {"g1": "1-4 weeks off.", "g2": "6 weeks off.", "g1_m": 1, "g2_m": 2}
        }
    }
}

st.title("🩺 Clinician's DVLA Assistant")

# --- HEADER: THE SAFETY CHECK ---
col_head1, col_head2 = st.columns([2, 1])
with col_head1:
    st.warning("⚠️ **Disclaimer:** This tool is a snapshot of Feb 2026 standards. Always verify the 'Source of Truth' below.")
with col_head2:
    st.info(f"📅 **App Version:** 1.0.4\n\n**Data Snapshot:** 10 Feb 2026")

# --- NAVIGATION ---
chapter_name = st.selectbox("Select Chapter:", list(DVLA_GUIDELINES.keys()))
chapter_data = DVLA_GUIDELINES[chapter_name]
condition_name = st.selectbox("Select Condition:", list(chapter_data["conditions"].keys()))

# --- THE LIVE BUTTON ---
st.link_button(f"🔗 Open Official {chapter_name} (Live GOV.UK)", chapter_data["url"])

# ... (Calculations and advice display logic remains the same)
