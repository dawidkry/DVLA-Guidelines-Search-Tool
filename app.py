import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards", page_icon="🩺", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display:none !important;}
    
    .dash-box { background-color: #000000; color: #ffffff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .ref-box { background-color: #f1f3f5; color: #1a1a1a; padding: 20px; border-left: 8px solid #005eb8; border-radius: 4px; font-size: 1.1em; }
    .disclaimer-banner { background-color: #440000; color: #FFCCCC; padding: 15px; border-radius: 5px; border: 2px solid #FF0000; text-align: center; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- THE FULL RESTORED CLINICAL DATABASE ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke (Single)": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. Resume if no residual deficit (motor, visual, or cognitive)."},
            "TIA / Stroke (Recurrent)": {"g1": "3 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Multiple events in short succession require 3 months cessation for Group 1."},
            "Epilepsy (Unprovoked)": {"g1": "12 months off.", "g2": "10 years off.", "notif": "Yes", "ref": "12 months standard. 6 months if low risk (<2% per annum). G2: 10 years free of meds."},
            "Seizure (Provoked - Acute Factor)": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Includes alcohol withdrawal or acute head injury seizure within 24h."},
            "Seizure (Sleep-only Pattern)": {"g1": "1-3 years stability.", "g2": "Revoked.", "notif": "Yes", "ref": "1 year if established sleep pattern; 3 years if pattern not yet stable."},
            "Subarachnoid Haemorrhage": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if successfully treated (coiled/clipped) and no deficit."},
            "Meningioma (Benign)": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if surgery performed and no seizures or deficit."},
            "Glioblastoma (Grade IV)": {"g1": "2 years off.", "g2": "Revoked.", "notif": "Yes", "ref": "2 years cessation from completion of primary treatment."},
            "Parkinson's Disease": {"g1": "Notify DVLA.", "g2": "Revoked.", "notif": "Yes", "ref": "Focus on motor control, 'off' periods, and cognitive stability."},
            "Narcolepsy / Cataplexy": {"g1": "Stop until controlled.", "g2": "Revoked.", "notif": "Yes", "ref": "Must cease until symptoms controlled and specialist confirms safety."},
            "Dementia / Cognitive Impairment": {"g1": "Notify/Review.", "g2": "Revoked.", "notif": "Yes", "ref": "Licensing depends on MoCA/MMSE scores and on-road assessment."},
            "Multiple Sclerosis": {"g1": "Notify DVLA.", "g2": "Revoked.", "notif": "Yes", "ref": "Usually 1-3 year medical review licenses granted if no disabling symptoms."},
        }
    },
    "Chapter 2: Cardiovascular & Syncope/TLoC": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Simple Vasovagal Syncope": {"g1": "No restriction.", "g2": "No restriction.", "notif": "No", "ref": "Must have clear prodrome while standing/sitting. Not allowed if occurred while driving."},
            "Unexplained TLoC (Low Risk)": {"g1": "6 months off.", "g2": "12 months off.", "notif": "Yes", "ref": "Single episode, normal ECG, no structural heart disease."},
            "Unexplained TLoC (High Risk)": {"g1": "12 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Abnormal ECG, exertional, or occurred while sitting/lying."},
            "Cough Syncope": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months from the last event for G1; 5 years for G2."},
            "Syncope (CV Cause Identified)": {"g1": "4 weeks off.", "g2": "3 months off.", "notif": "Yes", "ref": "Resume once underlying cause effectively treated (e.g. pacemaker)."},
            "Syncope (Postural Hypotension)": {"g1": "Stop until treated.", "g2": "3 months off.", "notif": "Yes", "ref": "May resume when symptoms resolved and BP controlled."},
            "ACS (PCI performed)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no other planned procedures."},
            "ICD (Symptomatic/Shock)": {"g1": "6 months off.", "g2": "Permanent Bar.", "notif": "Yes", "ref": "6 months from last shock. G2 is permanently disqualified."},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "1 week (G1) or 6 weeks (G2) following surgery."},
            "Aneurysm (Thoracic >6.5cm)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "G1 notify if >6.0cm. Disqualified if >6.5cm. G2 disqualified >5.5cm."},
            "Brugada Syndrome": {"g1": "No restriction.", "g2": "Notify/Review.", "notif": "G2 Yes", "ref": "G2 requires specialist report confirming low risk."},
            "Heart Failure (NYHA IV)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must not drive if symptoms occur at rest or minimal exertion."},
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Monitor glucose <2h before driving and every 2h while driving."},
            "Severe Hypoglycaemia (x2 in 12m)": {"g1": "12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "G1 revoked if 2 episodes requiring help occur in 1 year."},
            "Hypo Unawareness": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must regain awareness before license reinstatement."},
            "Metformin Only": {"g1": "No notification.", "g2": "No notification.", "notif": "No", "ref": "No notification unless severe hypos or visual complications occur."},
            "Sulfonylurea (Gliclazide)": {"g1": "No (usually).", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "G2 must notify for all insulin secretagogues."},
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Must be compliant and free from side effects."},
            "Mania / Bipolar": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Stability period starts from resolution of acute episode."},
            "Severe Depression": {"g1": "Clinical Pass.", "g2": "6 months stable.", "notif": "If severe", "ref": "Notify if symptoms affect concentration or involve suicidal ideation."},
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "1 year (G1) or 3 years (G2) abstinence or controlled drinking."},
            "Cannabis / Cocaine Misuse": {"g1": "6-12 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Clinical freedom from misuse for specified period."},
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Acuity Standard": {"g1": "6/12 + 20m plate.", "g2": "6/7.5 + 6/60.", "notif": "No", "ref": "Must read 79mm plate at 20m. Horizontal field 120 deg required."},
            "Glaucoma (Advanced)": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Licensing depends on binocular Esterman field test results."},
            "Diplopia": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Resume if controlled by patch or prisms."},
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP.", "g2": "Stop until CPAP.", "notif": "Yes", "ref": "Notify DVLA. Resume when CPAP control confirmed."},
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Age 70+": {"g1": "3yr renewal.", "g2": "N/A.", "notif": "Yes", "ref": "Must renew Group 1 license every 3 years from age 70."},
            "Abdominal Surgery": {"g1": "4-6 weeks off.", "g2": "Review.", "notif": "No", "ref": "Resume when emergency stop possible and pain-free."},
        }
    }
}

# --- DASHBOARD HEADER ---
st.markdown('<div class="dash-box"><h1>🩺 DVLA Clinical Standards Dashboard 2026</h1></div>', unsafe_allow_html=True)

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



st.markdown('<div class="disclaimer-banner"><strong>⚠️ DISCLAIMER:</strong> Decision-support only. Always verify at GOV.UK.</div>', unsafe_allow_html=True)
