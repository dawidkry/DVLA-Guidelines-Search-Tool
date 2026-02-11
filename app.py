import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards 2026", page_icon="🩺", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display:none !important;}
    
    .dash-box { background-color: #000000; color: #ffffff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .ref-box { background-color: #f1f3f5; color: #1a1a1a; padding: 20px; border-left: 8px solid #005eb8; border-radius: 4px; font-size: 1.1em; }
    .appendix-box { background-color: #e8f4f8; border: 1px solid #005eb8; padding: 15px; border-radius: 5px; }
    .disclaimer-banner { background-color: #440000; color: #FFCCCC; padding: 15px; border-radius: 5px; border: 2px solid #FF0000; text-align: center; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER DATABASE (Restored & Expanded) ---
DVLA_DATA = {
    "Appendix D: TLoC & Blackouts": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive#appendix-d-transient-loss-of-consciousness-blackouts-and-lost-or-altered-awareness",
        "conditions": {
            "Reflex Syncope (Reliable Prodrome) - Single": {"g1": "No ban (if not while driving).", "g2": "3 months off.", "notif": "G2 Yes / G1 No", "ref": "G1: If not while driving, may drive/no notify. If while driving, 1 month off/no notify. G2: 3 months off (if no provocation)."},
            "Reflex Syncope (No Prodrome) - Single": {"g1": "3 months off.", "g2": "12 months off.", "notif": "Yes", "ref": "G1: 3 months if no avoidable provocation. G2: 12 months off subject to specialist report."},
            "Unexplained TLoC (Single Episode)": {"g1": "6 months off.", "g2": "12 months off.", "notif": "Yes", "ref": "G1: 6 months off. G2: 12 months (revocation). Apply specific standard if cause found later."},
            "Unexplained TLoC (Multiple - 24m)": {"g1": "12 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Multiple episodes within 24 months where no cause is identified."},
            "Blackout with Seizure Markers (Isolated)": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Likely seizure (LOC >5m, tongue biting, injury, post-ictal confusion). 12 months off if high-risk factors."},
            "Cough Syncope (Single)": {"g1": "6 months off.", "g2": "12 months off.", "notif": "Yes", "ref": "Treatment of the cough does NOT reduce the risk. Standards apply from the date of episode."},
            "Cough Syncope (Multiple - 5yr)": {"g1": "12 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Multiple episodes over 5 years. 24hr cluster counts as one event."},
        }
    },
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke (Single)": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Resume after 1 month if no residual deficit (motor, visual, or cognitive)."},
            "Epilepsy (Unprovoked)": {"g1": "12 months off.", "g2": "10 years off.", "notif": "Yes", "ref": "12 months standard. 6 months if low risk (<2% per annum)."},
            "Dementia": {"g1": "Notify/Review.", "g2": "Revoked.", "notif": "Yes", "ref": "Licensing depends on MoCA scores and on-road assessment."},
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "ACS (Successful PCI)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no other planned procedures."},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "1 week (G1) or 6 weeks (G2) following surgery."},
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Monitor glucose <2h before driving and every 2h while driving."},
            "Severe Hypoglycaemia (x2 in 12m)": {"g1": "12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "G1 revoked if 2 episodes requiring help occur in 1 year."},
        }
    }
}

# --- DASHBOARD HEADER ---
st.markdown('<div class="dash-box"><h1>🩺 DVLA Clinical Navigator & Appendix D Matrix</h1></div>', unsafe_allow_html=True)

# CALCULATOR ROW
col_c1, col_c2, col_c3, col_c4 = st.columns([1.5, 1, 1, 1.5])
with col_c1: evt_date = st.date_input("🗓️ Date of Event:", value=date.today())
with col_c2: unit = st.radio("Unit:", ["Weeks", "Months"], horizontal=True)
with col_c3: num = st.number_input(f"No. {unit}:", min_value=0, value=1)
with col_c4:
    delta = timedelta(weeks=num) if unit == "Weeks" else timedelta(days=int(num * 30.44))
    res_date = evt_date + delta
    st.metric("Potential Resume Date", res_date.strftime('%d/%m/%Y'))

st.divider()

# --- APPENDIX D SPECIAL SECTION ---
with st.expander("📘 VIEW APPENDIX D: TLoC, BLACKOUTS & COUGH SYNCOPE DEFINITIONS", expanded=False):
    st.markdown("""
    ### Appendix D: Transient loss of consciousness (blackouts)
    **Definition:** TLoC is a state of real or apparent loss of consciousness with loss of awareness, amnesia, and abnormal motor control.
    
    #### 1. Reflex Syncope (Vasovagal)
    * **Reliable Prodrome:** A warning (sweating/heat) recognized by the driver of sufficient duration to safely stop the vehicle.
    * **Avoidable Provocation:** Factors like medical procedures or prolonged standing (e.g., soldier on parade).
    
    #### 2. Blackouts with Seizure Markers
    *On the balance of probability, clinical suspicion of a seizure.* Likely if:
    * LOC or amnesia > 5 minutes
    * Injury or Tongue Biting
    * Incontinence or Post-ictal confusion/headache.
    
    #### 3. Cough Syncope
    * **Crucial Rule:** Treatment of the underlying condition (e.g., infection) does **NOT** reduce the risk. Identification of cough syncope places the patient in a high-risk group indefinitely.
    """)

st.divider()

# SELECTOR & SOURCE LINK
c1, c2 = st.columns(2)
with c1: chap = st.selectbox("📁 System Chapter", options=list(DVLA_DATA.keys()))
with c2: cond = st.selectbox("🔬 Clinical Condition", options=list(DVLA_DATA[chap]["conditions"].keys()))

st.link_button(f"🔗 Open Official GOV.UK {chap}", DVLA_DATA[chap]["url"])

res = DVLA_DATA[chap]["conditions"][cond]

# RESULTS
v1, v2, v3 = st.columns([1, 1.5, 1.5])
with v1:
    notif_color = "#d32f2f" if "yes" in res['notif'].lower() else "#2e7d32"
    st.markdown(f"**🔔 Notifiable?**\n\n<span style='color:{notif_color}; font-size: 1.8em; font-weight: bold;'>{res['notif']}</span>", unsafe_allow_html=True)
with v2: st.info(f"**🚗 Group 1**\n\n{res['g1']}")
with v3: st.warning(f"**🚛 Group 2**\n\n{res['g2']}")

st.divider()
st.subheader("📖 Official Regulatory Reference")
st.markdown(f'<div class="ref-box">{res["ref"]}</div>', unsafe_allow_html=True)

st.divider()
st.subheader("🖋️ Proposed Medical Entry")
st.code(f"DVLA FITNESS TO DRIVE ASSESSMENT:\nClinical Context: {cond}\nRegulatory Guidance: {res['ref']}\nAdvice: Cease driving for {num} {unit.lower()} from {evt_date.strftime('%d/%m/%Y')}.\nEarliest Potential Resume: {res_date.strftime('%d/%m/%Y')}\nDVLA Notification Required: {res['notif']}.", language="text")

st.markdown('<div class="disclaimer-banner"><strong>⚠️ DISCLAIMER:</strong> Decision-support only. Verify at GOV.UK.</div>', unsafe_allow_html=True)
