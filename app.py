import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards 2026", page_icon="🩺", layout="wide")

# --- UI CLEANUP & STYLING (BLACK DASHBOARD) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display:none !important;}
    
    /* Dashboard Header Styling */
    .dash-box {
        background-color: #000000;
        color: #ffffff;
        padding: 25px;
        border-radius: 10px;
        margin-bottom: 25px;
    }
    .stMetric { background-color: #1a1a1a; padding: 10px; border-radius: 5px; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; }
    
    .ref-box {
        background-color: #f0f2f6; color: #1a1a1a; padding: 20px;
        border-left: 10px solid #005eb8; border-radius: 4px; font-size: 1.1em;
    }
    .disclaimer-banner {
        background-color: #440000; color: #FFCCCC; padding: 15px;
        border-radius: 5px; border: 2px solid #FF0000; text-align: center; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- THE MASTER CLINICAL DATABASE (COMPLETE 8 CHAPTERS) ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke (Single)": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. Resume after 1 month if no residual deficit."},
            "Epilepsy (Unprovoked)": {"g1": "12 months off.", "g2": "10 years off.", "notif": "Yes", "ref": "12 months standard. 6 months if low risk (<2% per annum). G2: 10 years off meds."},
            "Seizure (Alcohol/Drug Provoked)": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months from event (G1) or 5 years (G2). Requires clinical stability."},
            "Meningioma (Benign)": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if surgery/no seizure. Longer if radiotherapy used."},
            "Glioblastoma (Grade 4)": {"g1": "2 years off.", "g2": "Revoked.", "notif": "Yes", "ref": "2 years cessation from completion of primary treatment."},
            "Narcolepsy": {"g1": "Stop until controlled.", "g2": "Revoked.", "notif": "Yes", "ref": "Must not drive until symptoms controlled and specialist confirms safety."},
            "Dementia": {"g1": "Cognition-based.", "g2": "Revoked.", "notif": "Yes", "ref": "License granted if MMSE/MoCA scores and on-road test are satisfactory."},
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "ACS (Successful PCI)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no other planned procedures."},
            "ICD (Symptomatic/Shock)": {"g1": "6 months off.", "g2": "Permanent Bar.", "notif": "Yes", "ref": "6 months from shock. G2 is permanently disqualified."},
            "Aneurysm (Thoracic >6.0cm)": {"g1": "Notify/Stop.", "g2": "Stop.", "notif": "Yes", "ref": "G1 notify if >6.0cm. Disqualified if >6.5cm. G2 disqualified >5.5cm."},
            "Brugada Syndrome": {"g1": "No restriction.", "g2": "Specialist Review.", "notif": "G2 Yes", "ref": "G2 drivers must have specialist report confirming low risk."},
            "Heart Transplant": {"g1": "6 weeks off.", "g2": "3 months off.", "notif": "Yes", "ref": "Resume after 6w (G1) or 3m (G2) if clinically stable and specialist review."},
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin (G1)": {"g1": "Notify DVLA.", "g2": "N/A", "notif": "Yes", "ref": "Must test <2h before driving and every 2h while driving."},
            "Severe Hypoglycaemia (x2 in 12m)": {"g1": "12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "G1 revoked if 2 episodes requiring help occur in 1 year."},
            "Sulfonylurea (Gliclazide)": {"g1": "No (unless hypos).", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "G1 only if severe hypos occur. G2 must notify for all Sulphonylureas."},
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Must be compliant and free from adverse med side effects."},
            "Bipolar (Acute Mania)": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Resolution of episode required before stability clock starts."},
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "Abstinence or controlled drinking (G1=1yr, G2=3yrs)."},
            "Cocaine Misuse": {"g1": "1 year off.", "g2": "1 year off.", "notif": "Yes", "ref": "1 year free of misuse and clinical stability required."},
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Acuity Standard": {"g1": "6/12 + 20m plate.", "g2": "6/7.5 + 6/60.", "notif": "No", "ref": "Must read 79mm plate at 20m. Horizontal field 120 deg required."},
            "Hemianopia": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "G1 exceptional cases possible after 12 months stability."},
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP.", "g2": "Stop until CPAP.", "notif": "Yes", "ref": "Notify DVLA. Resume once control confirmed by specialist."},
            "Cough Syncope": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months (G1) or 5 years (G2) from the last event."},
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Age 70+": {"g1": "3yr renewal.", "g2": "N/A.", "notif": "Yes", "ref": "Group 1 must renew license every 3 years from age 70."},
        }
    }
}

# --- MAIN DASHBOARD SECTION ---
st.markdown('<div class="dash-box"><h1>🩺 DVLA Clinical Cessation Dashboard</h1></div>', unsafe_allow_html=True)

# TOP ROW: CALCULATOR (Instead of Sidebar)
col_calc_1, col_calc_2, col_calc_3, col_calc_4 = st.columns([1.5, 1, 1, 1.5])

with col_calc_1:
    evt_date = st.date_input("🗓️ Date of Clinical Event:", value=date.today())
with col_calc_2:
    unit = st.radio("Unit:", ["Weeks", "Months"], horizontal=True)
with col_calc_3:
    num = st.number_input(f"No. {unit}:", min_value=0, value=1)
with col_calc_4:
    delta = timedelta(weeks=num) if unit == "Weeks" else timedelta(days=int(num * 30.44))
    resume_date = evt_date + delta
    st.metric("Potential Resume Date", resume_date.strftime('%d/%m/%Y'))

st.markdown("---")

# MIDDLE ROW: CONDITION SELECTOR
c1, c2 = st.columns(2)
with c1: chap = st.selectbox("📁 Select System Chapter", options=list(DVLA_DATA.keys()))
with c2: cond = st.selectbox("🔬 Select Clinical Condition", options=list(DVLA_DATA[chap]["conditions"].keys()))

res = DVLA_DATA[chap]["conditions"][cond]
st.link_button(f"🔗 Open Official GOV.UK Guidance for {chap}", DVLA_DATA[chap]["url"])

# BOTTOM SECTION: CLINICAL VERDICT
st.divider()
col_notif, col_g1, col_g2 = st.columns([1, 1.5, 1.5])
with col_notif:
    notif_color = "#d32f2f" if "yes" in res['notif'].lower() else "#2e7d32"
    st.markdown(f"**🔔 Notifiable?**\n\n<span style='color:{notif_color}; font-size: 1.8em; font-weight: bold;'>{res['notif']}</span>", unsafe_allow_html=True)
with col_g1: st.info(f"**🚗 Group 1 (Car/Bike)**\n\n{res['g1']}")
with col_g2: st.warning(f"**🚛 Group 2 (HGV/Bus)**\n\n{res['g2']}")

st.divider()
st.subheader("📖 Official Regulatory Reference")
st.markdown(f'<div class="ref-box">{res["ref"]}</div>', unsafe_allow_html=True)



st.divider()
st.subheader("🖋️ Proposed Medical Entry")
st.code(f"DVLA FITNESS TO DRIVE ASSESSMENT:\nClinical Context: {cond}\nRegulatory Guidance: {res['ref']}\nAdvice: Cease driving for {num} {unit.lower()} from {evt_date.strftime('%d/%m/%Y')}.\nEarliest Potential Resume: {resume_date.strftime('%d/%m/%Y')}\nDVLA Notification Required: {res['notif']}.\nPatient informed of legal responsibility to notify DVLA if required.", language="text")



# FINAL PERMANENT DISCLAIMER
st.markdown(f"""
    <div class="disclaimer-banner">
        <strong>⚠️ CLINICAL DISCLAIMER</strong><br>
        This tool is for decision-support only. Always verify the latest standards at 
        <a href="https://www.gov.uk/guidance/assessing-fitness-to-drive-a-guide-for-medical-professionals" style="color:white; text-decoration:underline;">GOV.UK</a> 
        before advising patients. Updated: February 2026.
    </div>
""", unsafe_allow_html=True)
