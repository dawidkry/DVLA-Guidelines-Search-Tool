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
    
    .dash-box {
        background-color: #000000;
        color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .ref-box {
        background-color: #f1f3f5; color: #1a1a1a; padding: 20px;
        border-left: 8px solid #005eb8; border-radius: 4px; font-size: 1.1em;
    }
    .disclaimer-banner {
        background-color: #440000; color: #FFCCCC; padding: 15px;
        border-radius: 5px; border: 2px solid #FF0000; text-align: center; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- THE EXHAUSTIVE CLINICAL DATABASE ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke (Single)": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Resume after 1 month if no residual deficit. G2 must have no functional impairment and clear brain imaging."},
            "TIA / Stroke (Recurrent)": {"g1": "3 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Recurrent events within short period require 3 months cessation for G1."},
            "Epilepsy (Unprovoked)": {"g1": "12 months off.", "g2": "10 years off.", "notif": "Yes", "ref": "12 months standard. 6 months if low risk (<2% per annum). G2: 10 years free of meds."},
            "Seizure (Sleep-only)": {"g1": "1-3 years stability.", "g2": "Revoked.", "notif": "Yes", "ref": "Can drive after 1 year if established sleep-only pattern; otherwise 3 years."},
            "Seizure (Provoked - Acute Head Injury)": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Seizure within 24h of TBI or acute insult."},
            "Subarachnoid Haemorrhage": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if no deficit and successfully treated (e.g. coiling)."},
            "Meningioma (Grade I)": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if surgery performed and no deficit/seizure."},
            "Glioblastoma / Grade IV Glioma": {"g1": "2 years off.", "g2": "Revoked.", "notif": "Yes", "ref": "2 years cessation from completion of primary treatment."},
            "Parkinson's Disease": {"g1": "Pass medical.", "g2": "Revoked.", "notif": "Yes", "ref": "Focus on motor control and cognitive fluctuations."},
            "Narcolepsy / Cataplexy": {"g1": "Stop until controlled.", "g2": "Revoked.", "notif": "Yes", "ref": "Resume only when symptoms controlled and specialist confirms safety."},
            "Dementia / Cognitive Impairment": {"g1": "Notify/Review.", "g2": "Revoked.", "notif": "Yes", "ref": "Licensing depends on on-road assessment and MoCA scores."},
        }
    },
    "Chapter 2: Cardiovascular (incl. TLoC/Syncope)": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Simple Vasovagal Syncope": {"g1": "No restriction.", "g2": "No restriction.", "notif": "No", "ref": "Must have clear prodrome while standing/sitting. Prohibited if event occurred while driving."},
            "Unexplained TLoC (Low Risk)": {"g1": "6 months off.", "g2": "12 months off.", "notif": "Yes", "ref": "Single episode, low recurrence risk according to cardiology/neuro review."},
            "Unexplained TLoC (High Risk)": {"g1": "12 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "High risk features (e.g. ECG abnormality, no prodrome)."},
            "Cough Syncope": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months (G1) or 5 years (G2) from the last event."},
            "Syncope with identifiable CV cause": {"g1": "4 weeks off.", "g2": "3 months off.", "notif": "Yes", "ref": "Resume once underlying cause (e.g. bradycardia) is treated/controlled."},
            "ACS (PCI performed)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no other planned procedures."},
            "ICD (Symptomatic/Shock)": {"g1": "6 months off.", "g2": "Permanent Bar.", "notif": "Yes", "ref": "6 months from shock. G2 is permanently disqualified."},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "1 week (G1) or 6 weeks (G2) following surgery/battery change."},
            "Aneurysm (>6.5cm)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "G1 notify if >6.0cm. Disqualified if >6.5cm. G2 disqualified >5.5cm."},
            "Heart Failure (NYHA IV)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must not drive if symptoms occur at rest or minimal exertion."},
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Test glucose <2h before driving and every 2h while driving."},
            "Severe Hypoglycaemia (x2 in 12m)": {"g1": "12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "G1 revoked if 2 episodes requiring help occur in 1 year."},
            "Hypo Unawareness": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must regain awareness before license reinstatement."},
            "Sulfonylurea (e.g. Gliclazide)": {"g1": "No (unless hypos).", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "G2 must notify. G1 only if recurrent severe hypos occur."},
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Must be compliant and free from adverse med side effects."},
            "Mania / Hypomania": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Stability period starts from resolution of the acute episode."},
            "Severe Depression": {"g1": "Clinical Pass.", "g2": "6 months stable.", "notif": "If severe", "ref": "Notify if affects concentration or involves suicidal ideation."},
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "Requires abstinence or controlled drinking (G1=1yr, G2=3yrs)."},
            "Cannabis Misuse": {"g1": "6 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Persistent misuse: 6 months (G1) or 1 year (G2) free of use."},
            "Cocaine / Stimulants": {"g1": "1 year off.", "g2": "1 year off.", "notif": "Yes", "ref": "1 year free of misuse and clinical stability required."},
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Acuity Standard": {"g1": "6/12 + 20m plate.", "g2": "6/7.5 + 6/60.", "notif": "No", "ref": "Must read 79mm plate at 20m. Horizontal field 120 deg required."},
            "Hemianopia": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "G1 exceptions possible after 12 months stability/adaptation."},
            "Diplopia": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Resume once stable and controlled (patch/prisms)."},
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP.", "g2": "Stop until CPAP.", "notif": "Yes", "ref": "Resume when sleepiness controlled by CPAP confirmed by specialist."},
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Age 70+": {"g1": "3yr renewal.", "g2": "N/A.", "notif": "Yes", "ref": "Group 1 must renew license every 3 years from age 70."},
            "Abdominal Surgery": {"g1": "4-6 weeks off.", "g2": "Review.", "notif": "No", "ref": "Resume when emergency stop possible and pain-free."},
        }
    }
}

# --- CALCULATOR HEADER ---
st.markdown('<div class="dash-box"><h1>🩺 DVLA Cessation Dashboard 2026</h1></div>', unsafe_allow_html=True)
col_c1, col_c2, col_c3, col_c4 = st.columns([1.5, 1, 1, 1.5])

with col_c1: evt_date = st.date_input("🗓️ Date of Event:", value=date.today())
with col_c2: unit = st.radio("Unit:", ["Weeks", "Months"], horizontal=True)
with col_c3: num = st.number_input(f"No. {unit}:", min_value=0, value=1)
with col_c4:
    delta = timedelta(weeks=num) if unit == "Weeks" else timedelta(days=int(num * 30.44))
    res_date = evt_date + delta
    st.metric("Potential Resume Date", res_date.strftime('%d/%m/%Y'))

st.divider()

# --- SELECTOR ---
c1, c2 = st.columns(2)
with c1: chap = st.selectbox("📁 System Chapter", options=list(DVLA_DATA.keys()))
with c2: cond = st.selectbox("🔬 Clinical Condition", options=list(DVLA_DATA[chap]["conditions"].keys()))

res = DVLA_DATA[chap]["conditions"][cond]

# --- CLINICAL RESULTS ---
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
