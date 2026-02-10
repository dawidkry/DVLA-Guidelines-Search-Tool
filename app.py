import streamlit as st
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Standards 2026",
    page_icon="🩺",
    layout="wide"
)

# --- THE DATASET (8 CHAPTERS + URLS) ---
CHAPTER_LINKS = {
    "Chapter 1: Neurological": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
    "Chapter 2: Cardiovascular": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
    "Chapter 3: Diabetes": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
    "Chapter 4: Psychiatric": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
    "Chapter 5: Drug & Alcohol": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
    "Chapter 6: Vision": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
    "Chapter 7: Renal & Respiratory": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
    "Chapter 8: Miscellaneous": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive"
}

DVLA_GUIDELINES = {
    "Chapter 1: Neurological": {
        "TIA / Stroke": {"g1": "1 month off. Resume if no residual deficit.", "g2": "1 year off.", "notif": "No (unless residual deficit)"},
        "Syncope (Simple Faint)": {"g1": "No restriction if prodrome present.", "g2": "No restriction unless recurring.", "notif": "No"},
        "Syncope (Unexplained TLoC)": {"g1": "6-12 months off depending on risk.", "g2": "12 months off minimum.", "notif": "Yes"},
        "Epilepsy (First Seizure)": {"g1": "6 or 12 months off.", "g2": "5 years off.", "notif": "Yes"},
        "Parkinson's Disease": {"g1": "Drive if safe control maintained.", "g2": "Usually revoked.", "notif": "Yes"}
    },
    "Chapter 2: Cardiovascular": {
        "MI (STEMI/NSTEMI)": {"g1": "1 week (if PCI/LVEF>40%) else 4 weeks.", "g2": "6 weeks off.", "notif": "No (G1)"},
        "Pacemaker Implantation": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes"},
        "ICD (Prophylactic/Symptomatic)": {"g1": "1 to 6 months off.", "g2": "Permanent bar.", "notif": "Yes"},
        "Aortic Aneurysm (>6cm)": {"g1": "Notify. Disqualified if >6.5cm.", "g2": "Disqualified if >5.5cm.", "notif": "Yes"}
    },
    "Chapter 3: Diabetes": {
        "Insulin Treated": {"g1": "May drive if <1 severe hypo/year.", "g2": "Strict criteria; CGM allowed with backup.", "notif": "Yes"}
    },
    "Chapter 4: Psychiatric": {
        "Psychosis / Schizophrenia": {"g1": "3 months stability to resume.", "g2": "12 months stability.", "notif": "Yes"}
    },
    "Chapter 5: Drug & Alcohol": {
        "Alcohol Dependence": {"g1": "1 year abstinence.", "g2": "3 years abstinence.", "notif": "Yes"}
    },
    "Chapter 6: Vision": {
        "Visual Acuity Standard": {"g1": "6/12 and read plate at 20m.", "g2": "6/7.5 and 6/60 in poorer eye.", "notif": "If standard not met"}
    },
    "Chapter 7: Renal & Respiratory": {
        "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP control.", "g2": "Stop until compliance confirmed.", "notif": "Yes"}
    },
    "Chapter 8: Miscellaneous": {
        "Hepatic Encephalopathy": {"g1": "Must notify. Resume if treated.", "g2": "Revoked until stable.", "notif": "Yes"},
        "Post-Major Surgery": {"g1": "Usually 1-3 months. No notification.", "g2": "Occ Health review.", "notif": "No (<3m)"}
    }
}

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    h1 { color: #005eb8; }
    .stMetric { background: white; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🩺 DVLA Clinical Navigator (2026)")
st.caption("Peer-to-peer decision support for medical professionals.")

# --- NAVIGATION ---
col_chap, col_cond = st.columns(2)
with col_chap:
    selected_chapter = st.selectbox("📁 Select Chapter", options=list(DVLA_GUIDELINES.keys()))
    st.link_button(f"🔗 View Live {selected_chapter}", CHAPTER_LINKS[selected_chapter])

with col_cond:
    selected_condition = st.selectbox("🔬 Select Condition", options=list(DVLA_GUIDELINES[selected_chapter]["conditions"].keys()))

# --- SIDEBAR: DYNAMIC CALCULATOR ---
with st.sidebar:
    st.header("⏳ Cessation period")
    event_date = st.date_input("Date of Event/Diagnosis:", value=datetime.today())
    
    # Toggle for Weeks vs Months
    calc_unit = st.radio("Calculate in:", ["Weeks", "Months"], horizontal=True)
    
    if calc_unit == "Weeks":
        duration = st.number_input("Number of Weeks:", min_value=0, max_value=52, value=1)
        resume_date = event_date + timedelta(weeks=duration)
    else:
        duration = st.number_input("Number of Months:", min_value=0, max_value=60, value=1)
        # Using 30.44 days as an average month for accuracy
        resume_date = event_date + timedelta(days=int(duration * 30.44))
    
    st.metric("Earliest Resume Date", resume_date.strftime('%d/%m/%Y'))
    
    st.divider()
    st.markdown("### 📞 DVLA Support")
    st.write("Professional Enquiries: **0300 790 6806**")

# --- RESULTS DISPLAY ---
res = DVLA_GUIDELINES[selected_chapter]["conditions"][selected_condition]
st.divider()

# Notification Banner
notif_color = "#D32F2F" if "yes" in res['notif'].lower() else "#388E3C"
st.markdown(f"### Notification Status: <span style='color:{notif_color}'>{res['notif']}</span>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.info(f"**🚗 Group 1 (Car/Motorcycle)**\n\n{res['g1']}")
with c2:
    st.warning(f"**🚛 Group 2 (Bus/Lorry)**\n\n{res['g2']}")

# --- CLINICAL NOTE ---
st.divider()
st.subheader("🖋️ Proposed Medical Entry")
note = (
    f"Discussed DVLA fitness to drive (Chapter: {selected_chapter}). "
    f"Condition: {selected_condition}. "
    f"Advised cessation for {duration} {calc_unit.lower()} from {event_date.strftime('%d/%m/%Y')}. "
    f"Earliest return: {resume_date.strftime('%d/%m/%Y')}. "
    f"Notification required: {res['notif']}."
)
st.code(note, language="text")

st.divider()
st.caption("🚨 **Clinical Alert:** This tool uses a summary of 2026 standards. Refer to GOV.UK for complex comorbidities.")
