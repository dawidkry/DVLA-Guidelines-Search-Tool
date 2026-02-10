import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards 2026", page_icon="🩺", layout="wide")

# --- UI CLEANUP & STYLING ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stToolbar"] {display:none !important;}

    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] li {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: bold !important; font-size: 2rem !important; }
    [data-testid="stMetricLabel"] { color: #BBBBBB !important; }

    .disclaimer-sidebar {
        background-color: #330000; color: #FFCCCC; padding: 10px;
        border-radius: 5px; border: 1px solid #FF0000; font-size: 0.85em; margin-top: 20px;
    }
    .ref-box {
        background-color: #ffffff; color: #1a1a1a; padding: 20px;
        border: 2px solid #005eb8; border-radius: 8px; font-size: 1.05em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- THE MASSIVE 8-CHAPTER CLINICAL DATABASE ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke (Standard)": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. Resume after 1 month if no residual deficit. G2 must have no functional impairment and clear brain imaging for certain cases."},
            "Recurrent TIA/Stroke": {"g1": "3 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "If recurrent events occur within a short period, 3 months cessation is usually required for G1."},
            "Epilepsy (Unprovoked Seizure)": {"g1": "6-12 months off.", "g2": "5-10 years off.", "notif": "Yes", "ref": "6 months if low risk of recurrence; 12 months standard. G2 requires 10 years seizure-free without meds."},
            "Epilepsy (Provoked - e.g. Acute Head Injury)": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Provoked by a likely non-recurrent factor. 6 months if clinical risk is <2% per annum."},
            "Seizures (Sleep-only Pattern)": {"g1": "1-3 years stability.", "g2": "Revoked.", "notif": "Yes", "ref": "If seizures occur only while asleep, may drive after 1 year if established pattern, otherwise 3 years."},
            "Brain Tumour (Benign - e.g. Meningioma)": {"g1": "6-12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "Grade 1 meningioma treated with surgery: 6 months off (if no seizure/deficit)."},
            "Brain Tumour (Malignant - e.g. Glioma)": {"g1": "1-2 years off.", "g2": "Revoked.", "notif": "Yes", "ref": "Grade 2: 1 year. Grade 3/4: 2 years cessation from completion of primary treatment."},
            "Subarachnoid Haemorrhage (Spontaneous)": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "If no intervention or successfully coiled and no deficit."},
            "Parkinson's Disease": {"g1": "Pass medical.", "g2": "Revoked.", "notif": "Yes", "ref": "Must notify. Focus on motor control, side effects of L-Dopa, and cognitive fluctuations."},
            "Dementia / Alzheimers": {"g1": "Subject to review.", "g2": "Revoked.", "notif": "Yes", "ref": "May continue G1 if cognition allows; mandatory on-road assessment often required."},
            "Multiple Sclerosis": {"g1": "Notify DVLA.", "g2": "Revoked.", "notif": "Yes", "ref": "Only drive if no disabling symptoms and visual standards met."},
            "Head Injury (Major)": {"g1": "6-12 months off.", "g2": "Discretionary.", "notif": "Yes", "ref": "Depends on PTA (Post-Traumatic Amnesia) duration and presence of intracranial hematoma."},
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI / ACS (Successful PCI)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no other planned procedures."},
            "MI / ACS (Medical Mgmt only)": {"g1": "4 weeks off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "Mandatory 4 weeks for car drivers without intervention."},
            "Pacemaker (New/Box change)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "Must not drive for 1 week (G1) or 6 weeks (G2) following surgery."},
            "ICD (Prophylactic)": {"g1": "1 month off.", "g2": "Permanent bar.", "notif": "Yes", "ref": "G2 is permanently disqualified. G1 is 1 month if asymptomatic."},
            "ICD (Sustained VT / Shock)": {"g1": "6 months off.", "g2": "Permanent bar.", "notif": "Yes", "ref": "6 months from the date of the shock or event."},
            "Aortic Aneurysm (6.0-6.4cm)": {"g1": "Notify DVLA.", "g2": "Stop driving.", "notif": "Yes", "ref": "G1 can drive but must notify. G2 disqualified if >5.5cm."},
            "Aortic Aneurysm (>6.5cm)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "G1 must stop until surgically repaired."},
            "Heart Failure (NYHA I-III)": {"g1": "Drive if stable.", "g2": "Revoked if LVEF <40%.", "notif": "G2 Yes", "ref": "G2 drivers usually barred if LVEF <40% even if asymptomatic."},
            "Syncope (Simple Vasovagal)": {"g1": "No restriction.", "g2": "No restriction.", "notif": "No", "ref": "Must have clear prodrome while standing/sitting. Prohibited if event occurred while driving."},
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin (Group 1)": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Test <2h before driving and every 2h while driving. Must have 2 tests/day."},
            "Insulin (Group 2)": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Strict glucose monitoring. No more than 1 severe hypo in 12 months."},
            "Severe Hypoglycaemia (Group 1)": {"g1": "12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "Revoked if 2 episodes of severe hypo (requiring help) in 12 months."},
            "Severe Hypoglycaemia (Group 2)": {"g1": "Discretion.", "g2": "12 months off.", "notif": "Yes", "ref": "Single episode of severe hypo while awake is a 12-month ban for G2."},
            "Hypoglycaemia Unawareness": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must stop until awareness is regained to specialist satisfaction."},
            "Non-insulin (Sulphonylurea)": {"g1": "No restriction.", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "G1 only notifies if recurrent severe hypos occur."},
            "Gestational Diabetes (Insulin)": {"g1": "No notification.", "g2": "No notification.", "notif": "No", "ref": "Provided insulin stops after delivery and no hypos occur."},
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Must be stable on meds with no significant side effects."},
            "Hypomania / Mania": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Stable period starts after acute episode resolves."},
            "Severe Depression": {"g1": "Pass clinical.", "g2": "6 months stable.", "notif": "Only if severe", "ref": "Notify if concentration, agitation, or suicidal ideation is present."},
            "Bipolar Disorder": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Must notify and remain stable on/off medication."},
            "Personality Disorder": {"g1": "Discretion.", "g2": "Revoked (Severe).", "notif": "If risky", "ref": "Notify if behaviors likely to affect road safety (e.g. impulsivity)."},
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "1 year abstinence or controlled drinking (G1). G2 strictly 3 years."},
            "Alcohol Misuse": {"g1": "6 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Freedom from misuse for specified period (verified by CDT blood test)."},
            "Cannabis Misuse": {"g1": "6 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Persistent misuse: 6 months (G1) or 1 year (G2) free of use."},
            "Cocaine / Amphetamine": {"g1": "1 year off.", "g2": "1 year off.", "notif": "Yes", "ref": "Requires 1 year free of misuse and clinical stability."},
            "Opiate Dependence (Heroin)": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "Stability on methadone/buprenorphine may allow G1 licensing after 1 year."},
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Acuity Standard": {"g1": "6/12 + 20m plate.", "g2": "6/7.5 + 6/60.", "notif": "No (if met)", "ref": "Must read 79mm plate at 20m. Horizontal field of 120 deg required."},
            "Monocularity (Complete)": {"g1": "No restriction.", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "G2 must reach 6/7.5 in remaining eye and notify DVLA for assessment."},
            "Visual Field Defect (Stroke)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Hemianopia/Quadrantanopia: 12 months stability before 'exceptional' appeal possible."},
            "Diplopia (Uncorrected)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must stop until stable and controlled by a patch/prisms."},
            "Blepharospasm": {"g1": "Clinical discretion.", "g2": "Revoked.", "notif": "Yes", "ref": "Notify if severe enough to cause functional blindness while driving."},
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP.", "g2": "Stop until CPAP.", "notif": "Yes", "ref": "Must not drive if excessive sleepiness. Resume once CPAP control confirmed."},
            "Cough Syncope": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months off from the last episode. G2 strictly 5 years."},
            "Chronic Renal Failure": {"g1": "No restriction.", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "G2 drivers must notify; licensing subject to medical report."},
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Abdominal Surgery": {"g1": "Discretion.", "g2": "Clinical review.", "notif": "No", "ref": "Resume when able to perform emergency stop safely (usually 4-6 weeks)."},
            "Neurosurgery": {"g1": "6-12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "Depends on underlying pathology (tumour vs trauma)."},
            "Age 70+ (Group 1)": {"g1": "3yr renewal.", "g2": "N/A", "notif": "Renewal req", "ref": "Licences must be renewed every 3 years from age 70."},
            "Impaired Awareness (General)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Any condition causing significant cognitive or motor impairment."},
        }
    }
}

# --- NAVIGATION ---
st.title("🩺 DVLA Clinical Standards Navigator")
c1, c2 = st.columns(2)
with c1: chap = st.selectbox("📁 System Chapter", options=list(DVLA_DATA.keys()))
with c2: cond = st.selectbox("🔬 Clinical Condition", options=list(DVLA_DATA[chap]["conditions"].keys()))

st.link_button(f"🔗 Open Official GOV.UK {chap}", DVLA_DATA[chap]["url"])

# --- DATA ---
res = DVLA_DATA[chap]["conditions"][cond]

# --- SIDEBAR ---
with st.sidebar:
    st.header("⏳ Cessation Clock")
    evt_date = st.date_input("Date of Event:", value=date.today())
    unit = st.radio("Unit:", ["Weeks", "Months"], horizontal=True)
    num = st.number_input(f"Number of {unit}:", min_value=0, value=1)
    delta = timedelta(weeks=num) if unit == "Weeks" else timedelta(days=int(num * 30.44))
    resume = evt_date + delta
    st.metric("Resume Date", resume.strftime('%d/%m/%Y'))
    st.markdown("---")
    st.header("🏥 Quick Links")
    st.markdown("- [DVLA Professional Guide](https://www.gov.uk/guidance/assessing-fitness-to-drive-a-guide-for-medical-professionals)")
    st.markdown("""<div class="disclaimer-sidebar"><strong>⚠️ CLINICAL DISCLAIMER</strong><br>Decision-support only. Standards change. <strong>Always verify</strong> on GOV.UK.</div>""", unsafe_allow_html=True)

# --- VERDICT ---
st.divider()
col_notif, col_g1, col_g2 = st.columns([1, 1.5, 1.5])
with col_notif:
    notif_color = "#d32f2f" if "yes" in res['notif'].lower() else "#2e7d32"
    st.markdown(f"**🔔 Notifiable?**\n\n<span style='color:{notif_color}; font-size: 1.5em; font-weight: bold;'>{res['notif']}</span>", unsafe_allow_html=True)
with col_g1: st.info(f"**🚗 Group 1**\n\n{res['g1']}")
with col_g2: st.warning(f"**🚛 Group 2**\n\n{res['g2']}")

st.divider()
st.subheader("📖 Official Regulatory Reference")
st.markdown(f'<div class="ref-box">{res["ref"]}</div>', unsafe_allow_html=True)



st.divider()
st.subheader("🖋️ Proposed Medical Entry")
st.code(f"DVLA FITNESS TO DRIVE ASSESSMENT:\nClinical Context: {cond}\nRegulatory Guidance: {res['ref']}\nAdvice: Cease driving for {num} {unit.lower()} from {evt_date.strftime('%d/%m/%Y')}.\nEarliest Potential Resume: {resume.strftime('%d/%m/%Y')}\nDVLA Notification Required: {res['notif']}.\nPatient informed of legal responsibility to notify DVLA if required.", language="text")
