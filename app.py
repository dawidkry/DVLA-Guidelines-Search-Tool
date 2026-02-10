import streamlit as st
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Standards 2026",
    page_icon="🩺",
    layout="wide"
)

# --- THE COMPLETE DATASET (8 CHAPTERS) ---
DVLA_GUIDELINES = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {"g1": "1 month off. Resume if no residual deficit.", "g2": "1 year off. Requires stable imaging.", "notif": "No (unless residual deficit)", "m_g1": 1, "m_g2": 12},
            "Syncope (Simple Faint)": {"g1": "No restriction if prodrome present.", "g2": "No restriction unless recurring/no prodrome.", "notif": "No", "m_g1": 0, "m_g2": 0},
            "Syncope (Unexplained TLoC)": {"g1": "6 months off (low risk) or 12 months (high risk).", "g2": "12 months off minimum.", "notif": "Yes", "m_g1": 6, "m_g2": 12},
            "Epilepsy (First Seizure)": {"g1": "6 or 12 months off (specialist review).", "g2": "5 years off. 10 years seizure-free (no meds).", "notif": "Yes", "m_g1": 6, "m_g2": 60},
            "Brain Tumour": {"g1": "Dependent on grade/location. Usually 6-12 months.", "g2": "Usually permanent bar for Group 2.", "notif": "Yes", "m_g1": 12, "m_g2": 60},
            "Parkinson's Disease": {"g1": "Drive as long as safe control maintained.", "g2": "Usually revoked unless very mild.", "notif": "Yes", "m_g1": 0, "m_g2": 0},
            "Dementia / Cognitive Impairment": {"g1": "Must not drive if impairment affects safety.", "g2": "Permanent revocation.", "notif": "Yes", "m_g1": 0, "m_g2": 0}
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI (STEMI/NSTEMI)": {"g1": "1 week (if PCI/LVEF>40%) else 4 weeks.", "g2": "6 weeks off. Needs exercise test.", "notif": "No (G1)", "m_g1": 1, "m_g2": 2},
            "Angina (Symptomatic)": {"g1": "Stop driving when symptoms occur.", "g2": "Revoked until symptoms controlled for 6 weeks.", "notif": "No (G1)", "m_g1": 1, "m_g2": 2},
            "Pacemaker Implantation": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "m_g1": 1, "m_g2": 2},
            "ICD (Prophylactic/Symptomatic)": {"g1": "1 to 6 months off (indication dependent).", "g2": "Permanent bar.", "notif": "Yes", "m_g1": 6, "m_g2": 60},
            "Aortic Aneurysm (>6cm)": {"g1": "Must notify. Disqualified if >6.5cm.", "g2": "Disqualified if >5.5cm.", "notif": "Yes", "m_g1": 0, "m_g2": 0},
            "Heart Failure (NYHA IV)": {"g1": "Must not drive.", "g2": "Must not drive.", "notif": "Yes", "m_g1": 0, "m_g2": 0}
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated (on CGM)": {"g1": "CGM permitted. No more than 1 severe hypo/year.", "g2": "CGM permitted but finger-prick backup required.", "notif": "Yes", "m_g1": 0, "m_g2": 0},
            "Severe Hypoglycaemia": {"g1": "Revoked for 1 year after 2nd episode.", "g2": "Revoked for 1 year after 1st episode.", "notif": "Yes", "m_g1": 12, "m_g2": 12},
            "Hypo Unawareness": {"g1": "Must not drive until awareness returns.", "g2": "Permanent revocation.", "notif": "Yes", "m_g1": 12, "m_g2": 60}
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "Stable for 3 months to resume.", "g2": "Stable for 12 months to resume.", "notif": "Yes", "m_g1": 3, "m_g2": 12},
            "Severe Depression/Anxiety": {"g1": "Notify if concentration/suicidal ideation present.", "g2": "Revoked until 6 months stability.", "notif": "Yes", "m_g1": 1, "m_g2": 6},
            "ADHD / Autism": {"g1": "Notify only if affects driving.", "g2": "Individual assessment.", "notif": "Only if symptomatic", "m_g1": 0, "m_g2": 0}
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year abstinence/controlled drinking.", "g2": "3 years abstinence.", "notif": "Yes", "m_g1": 12, "m_g2": 36},
            "Drug Misuse (Cannabis/Cocaine)": {"g1": "6 months off (must be drug-free).", "g2": "1 year off (must be drug-free).", "notif": "Yes", "m_g1": 6, "m_g2": 12}
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Visual Acuity Standard": {"g1": "6/12 and read plate at 20m.", "g2": "6/7.5 and 6/60 in poorer eye.", "notif": "If standard not met", "m_g1": 0, "m_g2": 0},
            "Visual Field Defect": {"g1": "120 deg horizontal field required.", "g2": "160 deg horizontal field required.", "notif": "Yes", "m_g1": 0, "m_g2": 0},
            "Diplopia": {"g1": "Must not drive. Resume if patched/stable.", "g2": "Revoked until stable for 3 months.", "notif": "Yes", "m_g1": 1, "m_g2": 3}
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP control confirmed.", "g2": "Stop until CPAP compliance confirmed.", "notif": "Yes", "m_g1": 1, "m_g2": 3},
            "COPD/Asthma": {"g1": "No restriction unless syncopal cough.", "g2": "No restriction unless causing incapacity.", "notif": "No", "m_g1": 0, "m_g2": 0},
            "Chronic Renal Failure": {"g1": "No restriction unless significant fatigue.", "g2": "Revoked if causing incapacity.", "notif": "No", "m_g1": 0, "m_g2": 0}
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Hepatic Encephalopathy": {"g1": "Must notify. Resume if treated.", "g2": "Revoked until long-term stability.", "notif": "Yes", "m_g1": 6, "m_g2": 12},
            "Post-Major Surgery": {"g1": "Usually 1-3 months. No notification.", "g2": "Occupational health review.", "notif": "No (<3m)", "m_g1": 1, "m_g2": 2},
            "Deafness": {"g1": "No restriction.", "g2": "Individual assessment.", "notif": "No", "m_g1": 0, "m_g2": 0}
        }
    }
}

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f0f4f7; }
    h1 { color: #005eb8; }
    .stMetric { background: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🩺 Comprehensive DVLA Standards (2026)")
st.caption("Organized by Official Chapters | Decision-Support for Medical Professionals")

# --- NAVIGATION ---
col_chap, col_cond = st.columns(2)
with col_chap:
    chapter = st.selectbox("📁 Select System / Chapter", options=list(DVLA_GUIDELINES.keys()))
    st.link_button("🔗 Open Official GOV.UK Chapter", DVLA_GUIDELINES[chapter]["url"])
with col_cond:
    condition = st.selectbox("🔬 Select Specific Condition", options=list(DVLA_GUIDELINES[chapter]["conditions"].keys()))

# --- SIDEBAR CALCULATOR ---
data = DVLA_GUIDELINES[chapter]["conditions"][condition]
with st.sidebar:
    st.header("📅 Timeline Calc")
    group = st.radio("License Group:", ["Group 1 (Cars)", "Group 2 (HGV/Bus)"])
    event_date = st.date_input("Event Date:", value=datetime.today())
    
    # Auto-populate duration based on Group
    dur_val = data["m_g1"] if "Group 1" in group else data["m_g2"]
    duration = st.number_input("Cessation (Months):", value=dur_val)
    
    resume_date = event_date + timedelta(days=duration * 30)
    st.metric("Earliest Resume Date", resume_date.strftime('%d/%m/%Y'))
    st.divider()
    st.info("💡 **Clinical Tip:** Ensure the patient is informed that this is the *earliest* date, subject to clinical stability.")

# --- RESULTS ---
st.divider()
notif_col = "red" if "yes" in data["notif"].lower() else "green"
st.markdown(f"### Notification to DVLA: <span style='color:{notif_col}'>{data['notif']}</span>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.info(f"**🚗 Group 1 Standard**\n\n{data['g1']}")
with c2:
    st.warning(f"**🚛 Group 2 Standard**\n\n{data['g2']}")

# --- AUTO-NOTE ---
st.divider()
st.subheader("🖋️ Discharge / Clinic Note Snippet")
note = (
    f"ADVICE ON FITNESS TO DRIVE ({chapter}): Regarding {condition}. "
    f"Patient advised to cease driving for {duration} month(s) as per DVLA {group} standards. "
    f"Earliest resume date: {resume_date.strftime('%d/%m/%Y')}. "
    f"Legal responsibility to notify the DVLA discussed: {data['notif']}."
)
st.code(note, language="text")

st.divider()
st.caption("⚠️ **Verification:** Medical guidelines are subject to change. Use the link above to check the 'Assessing fitness to drive' guide for rare or complex comorbidities.")
