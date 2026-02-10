import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards 2026", page_icon="🩺", layout="wide")

# --- STYLING (THE BLACK SIDEBAR / WHITE TEXT ENGINE) ---
st.markdown("""
    <style>
    /* 1. Sidebar: Solid Black Background */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }
    
    /* 2. Sidebar Text & Headers: Pure White */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2 {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    
    /* 3. Sidebar Inputs: White Background, Black Text (Contrast Fix) */
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 4. Metric Value: High Contrast White */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 2rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #BBBBBB !important;
    }

    /* 5. Main Page Reference Box */
    .ref-box {
        background-color: #ffffff;
        color: #1a1a1a;
        padding: 20px;
        border: 2px solid #005eb8;
        border-radius: 8px;
        font-size: 1.05em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- THE MASSIVE CLINICAL DATABASE ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. May resume after 1 month if no residual neurological deficit. Notify only if deficit persists."},
            "Epilepsy (Isolated Seizure)": {"g1": "6-12 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months off if scans/EEG are clear. 12 months off if there is an underlying risk/lesion."},
            "Epilepsy (Chronic)": {"g1": "1 year seizure free.", "g2": "10 years seizure free.", "notif": "Yes", "ref": "Must be 12 months free of any seizure (unless asleep-only pattern for 1-3 years)."},
            "Syncope (Vasovagal)": {"g1": "No restriction.", "g2": "No restriction.", "notif": "No", "ref": "If clear prodrome and occurred while standing/sitting. No driving if event occurred while driving."},
            "Syncope (Unexplained TLoC)": {"g1": "6-12 months off.", "g2": "12 months off.", "notif": "Yes", "ref": "6 months if low risk; 12 months if high risk or recurrent."},
            "Parkinson’s Disease": {"g1": "Pass medical.", "g2": "Revoked.", "notif": "Yes", "ref": "Must notify. Licensing depends on maintaining safe control and absence of significant motor fluctuations."},
            "Dementia / Cognitive Impairment": {"g1": "Cognition dependent.", "g2": "Revoked.", "notif": "Yes", "ref": "Licence may be granted subject to annual review and/or on-road assessment."},
            "Multiple Sclerosis": {"g1": "Pass medical.", "g2": "Revoked.", "notif": "Yes", "ref": "Must notify. Prohibited if sudden disabling symptoms occur."},
            "Brain Tumour (Benign)": {"g1": "6-12 months off.", "g2": "Permanent/Long term.", "notif": "Yes", "ref": "Depends on histology and location. Grade 1 meningioma usually 6 months off (G1)."},
            "Subarachnoid Haemorrhage": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if no intervention or successful coiling."}
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "ACS (PCI performed)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no other planned procedures."},
            "ACS (No PCI)": {"g1": "4 weeks off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "4 weeks mandatory cessation for Group 1."},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "Includes new implants and battery/box changes."},
            "ICD (Prophylactic)": {"g1": "1 month off.", "g2": "Permanent bar.", "notif": "Yes", "ref": "Group 2 is permanently disqualified from holding a vocational licence."},
            "ICD (Symptomatic/Shock)": {"g1": "6 months off.", "g2": "Permanent bar.", "notif": "Yes", "ref": "6 months off from the last shock or event date."},
            "Aortic Aneurysm": {"g1": ">6.5cm Stop.", "g2": ">5.5cm Stop.", "notif": "Yes", "ref": "Notify if >6.0cm (G1) or >5.5cm (G2)."},
            "Atrial Fibrillation": {"g1": "No restriction.", "g2": "Symptom dependent.", "notif": "No", "ref": "May drive if no symptoms cause incapacity/distraction."},
            "Heart Failure (NYHA IV)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must not drive if symptoms occur at rest or with minimal exertion."}
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Must test glucose <2h before driving and every 2h while driving. Must have 2 per day when not driving."},
            "Severe Hypoglycaemia (G1)": {"g1": "12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "Revoked if 2 episodes of severe hypo (requiring help) occur in 12 months."},
            "Severe Hypoglycaemia (G2)": {"g1": "Discretion.", "g2": "12 months off.", "notif": "Yes", "ref": "Group 2: Revoked for 12 months following a single episode of severe hypo."},
            "Hypo Unawareness": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must stop driving until awareness is regained to specialist satisfaction."}
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Must be stable on meds, compliant, and free from significant side effects."},
            "Hypomania / Mania": {"g1": "Stable 3 months.", "g2": "Stable 12 months.", "notif": "Yes", "ref": "Licence revoked during acute episodes."},
            "Severe Depression": {"g1": "Pass clinical.", "g2": "6 months stable.", "notif": "Yes", "ref": "Only notify if affects concentration, agitation, or suicidal ideation."},
            "ADHD / ASD": {"g1": "No (usually).", "g2": "No (usually).", "notif": "Only if impaired", "ref": "Notify only if condition or medication causes functional impairment in driving ability."}
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "1 year of abstinence or controlled drinking required for G1."},
            "Alcohol Misuse": {"g1": "6 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Must be free from misuse for 6 months (G1) or 1 year (G2)."},
            "Drug Misuse (Group A)": {"g1": "6-12 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Includes Cannabis and Cocaine misuse. Requires clean urine/hair tests usually."}
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Visual Acuity Standard": {"g1": "6/12 and 20m plate.", "g2": "6/7.5 and 6/60.", "notif": "No (if met)", "ref": "Must read 79mm plate at 20m. Field of 120 degrees horizontal required."},
            "Visual Field Defect": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Includes hemianopia and quadrantanopia. Requires Esterman field test for appeal."},
            "Diplopia": {"g1": "Stop until stable.", "g2": "Stop until stable.", "notif": "Yes", "ref": "May resume if controlled by a patch or prisms (specialist confirmation needed)."},
            "Monocular Vision": {"g1": "No restriction.", "g2": "Notify DVLA.", "notif": "G2 Yes / G1 No", "ref": "G1 can drive if acuity/field are met in the remaining eye. G2 must notify."}
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until controlled.", "g2": "Stop until controlled.", "notif": "Yes", "ref": "Must not drive if excessive sleepiness. May resume once CPAP control confirmed."},
            "COPD / Asthma": {"g1": "No restriction.", "g2": "No restriction.", "notif": "No", "ref": "Unless symptoms (e.g., cough syncope) occur or extreme fatigue."},
            "Renal Failure (Dialysis)": {"g1": "No restriction.", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "Group 2 must notify. Licensing subject to satisfactory medical reports."}
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Post-Surgery (General)": {"g1": "Discretion.", "g2": "Occ Health review.", "notif": "No (<3m)", "ref": "Notify only if medical restrictions likely to exceed 3 months."},
            "Medication Side Effects": {"g1": "Stop until stable.", "g2": "Stop until stable.", "notif": "No", "ref": "It is the driver's responsibility not to drive if impaired by medication (e.g., opiates, sedatives)."},
            "Age (70+)": {"g1": "3-year renewal.", "g2": "Annual medical.", "notif": "Renewal req", "ref": "Licences must be renewed every 3 years from age 70."}
        }
    }
}

# --- NAVIGATION ---
st.title("🩺 DVLA Clinical Standards Navigator (Complete)")
c_col1, c_col2 = st.columns(2)
with c_col1:
    chap = st.selectbox("📁 System Chapter", options=list(DVLA_DATA.keys()))
with c_col2:
    cond = st.selectbox("🔬 Clinical Condition", options=list(DVLA_DATA[chap]["conditions"].keys()))

st.link_button(f"🔗 Source: {chap} (GOV.UK)", DVLA_DATA[chap]["url"])

# --- DATA RETRIEVAL ---
res = DVLA_DATA[chap]["conditions"][cond]

# --- SIDEBAR CALCULATOR (THE BLACK UI) ---
with st.sidebar:
    st.header("⏳ Cessation Clock")
    evt_date = st.date_input("Date of Event:", value=date.today())
    unit = st.radio("Unit:", ["Weeks", "Months"], horizontal=True)
    num = st.number_input(f"Number of {unit}:", min_value=0, value=1)
    
    delta = timedelta(weeks=num) if unit == "Weeks" else timedelta(days=int(num * 30.44))
    resume = evt_date + delta
    
    st.metric("Resume Date", resume.strftime('%d/%m/%Y'))
    st.markdown("---")
    st.write("Ensure you document the advice given to the patient in the notes.")

# --- MAIN CLINICAL VERDICT ---
st.divider()
col_notif, col_g1, col_g2 = st.columns([1, 1.5, 1.5])

with col_notif:
    notif_color = "#d32f2f" if "yes" in res['notif'].lower() else "#2e7d32"
    st.markdown(f"**🔔 Notifiable?**\n\n<span style='color:{notif_color}; font-size: 1.5em; font-weight: bold;'>{res['notif']}</span>", unsafe_allow_html=True)

with col_g1:
    st.info(f"**🚗 Group 1 (Car/Bike)**\n\n{res['g1']}")

with col_g2:
    st.warning(f"**🚛 Group 2 (HGV/Bus)**\n\n{res['g2']}")

# --- OFFICIAL REFERENCE ---
st.divider()
st.subheader("📖 Official Regulatory Reference")
st.markdown(f'<div class="ref-box">{res["ref"]}</div>', unsafe_allow_html=True)

# --- MEDICAL NOTE (AUTO-GENERATED) ---
st.divider()
st.subheader("🖋️ Proposed Medical Entry")
st.code(f"DVLA FITNESS TO DRIVE ASSESSMENT:\nClinical Context: {cond}\nRegulatory Guidance: {res['ref']}\nAdvice: Cease driving for {num} {unit.lower()} from {evt_date.strftime('%d/%m/%Y')}.\nEarliest Potential Resume: {resume.strftime('%d/%m/%Y')}\nDVLA Notification Required: {res['notif']}.\nPatient informed of legal responsibility to notify DVLA if required.", language="text")
