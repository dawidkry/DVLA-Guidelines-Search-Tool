import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Standards 2026",
    page_icon="🩺",
    layout="wide"
)

# --- THE DATASET (8 CHAPTERS - FULLY EXPANDED) ---
DVLA_GUIDELINES = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {"g1": "1 month off. Resume if no residual deficit.", "g2": "1 year off. Requires stable imaging.", "notif": "No (unless residual deficit)"},
            "Syncope (Simple Vasovagal)": {"g1": "No restriction if prodrome present.", "g2": "No restriction unless occurring while sitting/standing.", "notif": "No"},
            "Syncope (Unexplained TLoC)": {"g1": "6 months off (low risk) or 12 months (high risk).", "g2": "12 months off minimum.", "notif": "Yes"},
            "Cough Syncope": {"g1": "Stop driving until controlled. Notify DVLA.", "g2": "Licence revoked until asymptomatic for 3 months.", "notif": "Yes"},
            "Epilepsy (First Seizure)": {"g1": "6 or 12 months off (specialist review).", "g2": "5 years off. 10 years seizure-free (no meds).", "notif": "Yes"},
            "Brain Tumour (Benign/Malignant)": {"g1": "Usually 6-12 months off depending on grade/surgery.", "g2": "Usually permanent bar.", "notif": "Yes"},
            "Parkinson's Disease": {"g1": "Drive as long as safe control maintained.", "g2": "Usually revoked unless very mild.", "notif": "Yes"},
            "Dementia / Cognitive Impairment": {"g1": "Must not drive if impairment affects safety.", "g2": "Permanent revocation.", "notif": "Yes"},
            "Multiple Sclerosis": {"g1": "Notify. May drive if no sudden disabling symptoms.", "g2": "Individual assessment by DVLA.", "notif": "Yes"}
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI (STEMI/NSTEMI)": {"g1": "1 week (if PCI/LVEF>40%) else 4 weeks.", "g2": "6 weeks off. Needs exercise test.", "notif": "No (G1)"},
            "Angina (Symptomatic)": {"g1": "Stop driving when symptoms occur.", "g2": "Revoked until symptoms controlled for 6 weeks.", "notif": "No (G1)"},
            "Pacemaker Implantation": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes"},
            "ICD (Prophylactic/Symptomatic)": {"g1": "1 to 6 months off (indication dependent).", "g2": "Permanent bar.", "notif": "Yes"},
            "Aortic Aneurysm (>6.5cm)": {"g1": "Must stop driving. Disqualified if >6.5cm.", "g2": "Disqualified if >5.5cm.", "notif": "Yes"},
            "Heart Failure (NYHA IV)": {"g1": "Must not drive.", "g2": "Must not drive.", "notif": "Yes"},
            "Valvular Heart Disease": {"g1": "No restriction unless symptomatic.", "g2": "Revoked if NYHA functional class symptoms present.", "notif": "If symptomatic"}
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated (on CGM)": {"g1": "CGM permitted. No more than 1 severe hypo/year.", "g2": "CGM permitted but finger-prick backup required.", "notif": "Yes"},
            "Severe Hypoglycaemia": {"g1": "Revoked for 1 year after 2nd episode.", "g2": "Revoked for 1 year after 1st episode.", "notif": "Yes"},
            "Hypo Unawareness": {"g1": "Must not drive until awareness returns.", "g2": "Permanent revocation.", "notif": "Yes"}
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "Stable for 3 months to resume.", "g2": "Stable for 12 months to resume.", "notif": "Yes"},
            "Severe Depression/Anxiety": {"g1": "Notify if concentration/suicidal ideation present.", "g2": "Revoked until 6 months stability.", "notif": "Yes (if symptomatic)"},
            "Bipolar Disorder": {"g1": "No driving during acute episode. Stable for 3m.", "g2": "Stable for 6-12m to resume.", "notif": "Yes"}
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year abstinence/controlled drinking.", "g2": "3 years abstinence.", "notif": "Yes"},
            "Drug Misuse (Cannabis/Cocaine)": {"g1": "6 months off (must be drug-free).", "g2": "1 year off (must be drug-free).", "notif": "Yes"}
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Visual Acuity Standard": {"g1": "6/12 and read plate at 20m.", "g2": "6/7.5 and 6/60 in poorer eye.", "notif": "If standard not met"},
            "Visual Field Defect": {"g1": "120 deg horizontal field required.", "g2": "160 deg horizontal field required.", "notif": "Yes"},
            "Diplopia": {"g1": "Must not drive until stable or patched.", "g2": "Revoked until stable for 3 months.", "notif": "Yes"}
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP control confirmed.", "g2": "Stop until CPAP compliance confirmed.", "notif": "Yes"},
            "Chronic Renal Failure": {"g1": "No restriction unless significant fatigue.", "g2": "Revoked if causing incapacity.", "notif": "No"}
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Hepatic Encephalopathy": {"g1": "Must notify. Resume if treated.", "g2": "Revoked until long-term stability.", "notif": "Yes"},
            "Post-Major Surgery": {"g1": "Follow clinical advice (1-3 months).", "g2": "Occ Health review recommended.", "notif": "No (<3m)"}
        }
    }
}

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    h1 { color: #005eb8; font-family: 'Helvetica'; }
    .stSelectbox label { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🩺 Complete DVLA Navigator 2026")

# --- NAVIGATION ---
col_chap, col_cond = st.columns(2)

with col_chap:
    selected_chapter = st.selectbox("📁 Select Chapter", options=list(DVLA_GUIDELINES.keys()), key="chap_select")
    st.link_button(f"🔗 View Live {selected_chapter}", DVLA_GUIDELINES[selected_chapter]["url"])

with col_cond:
    # This prevents the KeyError by ensuring we always fetch from the active chapter selection
    condition_list = list(DVLA_GUIDELINES[selected_chapter]["conditions"].keys())
    selected_condition = st.selectbox("🔬 Select Condition", options=condition_list, key="cond_select")

# --- SIDEBAR: UNIT SELECTOR ---
with st.sidebar:
    st.header("⏳ Cessation Calculation")
    event_date = st.date_input("Date of Event:", value=date.today())
    
    # User's requested Weeks/Months toggle
    calc_unit = st.radio("Calculate in:", ["Weeks", "Months"], horizontal=True)
    
    if calc_unit == "Weeks":
        duration = st.number_input("Number of Weeks:", min_value=0, max_value=52, value=4)
        resume_date = event_date + timedelta(weeks=duration)
    else:
        duration = st.number_input("Number of Months:", min_value=0, max_value=60, value=1)
        resume_date = event_date + timedelta(days=int(duration * 30.44))
    
    st.metric("Earliest Resume Date", resume_date.strftime('%d/%m/%Y'))
    st.divider()
    st.caption("Standard cessation: 1 month (4 weeks) for many Group 1 neurological events.")

# --- RESULTS ---
if selected_condition in DVLA_GUIDELINES[selected_chapter]["conditions"]:
    res = DVLA_GUIDELINES[selected_chapter]["conditions"][selected_condition]
    st.divider()
    
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
        f"DVLA FITNESS TO DRIVE: Discussed {selected_condition}. "
        f"Advised cessation for {duration} {calc_unit.lower()} from {event_date.strftime('%d/%m/%Y')}. "
        f"Earliest return date: {resume_date.strftime('%d/%m/%Y')}. "
        f"Requirement to notify DVLA: {res['notif']}."
    )
    st.code(note, language="text")

st.divider()
st.caption("🚨 **Clinician Alert:** This is a summary. Always check the live link for comorbidities or complex cases.")
