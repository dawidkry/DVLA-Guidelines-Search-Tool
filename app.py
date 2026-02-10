import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards 2026", page_icon="🩺", layout="wide")

# --- STYLING (THE THEME-FIXER) ---
st.markdown("""
    <style>
    /* 1. Force Sidebar Background and Text Visibility */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6 !important;
    }
    [data-testid="stSidebar"] * {
        color: #000000 !important; /* Forces all text in sidebar to Black */
    }
    
    /* 2. Fix Metric Value specifically (The Resume Date) */
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 1.8rem !important;
    }

    /* 3. Reference Box Styling */
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

# --- EXPANDED DATABASE ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. May resume after 1 month if no residual deficit. Notify DVLA only if residual neurological deficit persists (visual field, cognition, or limb function)."},
            "Syncope (Simple Vasovagal)": {"g1": "No restriction.", "g2": "No restriction.", "notif": "No", "ref": "No restriction if there is a clear prodrome and the event occurred while standing/sitting. Prohibited if occurred while driving."},
            "Syncope (Unexplained TLoC)": {"g1": "6-12 months off.", "g2": "12 months off.", "notif": "Yes", "ref": "Unexplained syncope: 6 months off (G1) or 12 months if high-risk features present. Group 2 is 12 months off."},
            "Epilepsy (First Seizure)": {"g1": "6-12 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months off if scans/EEG are clear. 12 months off if there is an underlying risk or brain lesion."},
            "Provoked Seizure (e.g. Alcohol/Trauma)": {"g1": "Clinical discretion.", "g2": "Discretion/5yrs.", "notif": "Yes", "ref": "Must notify. Cessation depends on the specific provocation factor and specialist input."},
            "Brain Tumour (Malignant)": {"g1": "1-2 years off.", "g2": "Permanent bar.", "notif": "Yes", "ref": "Grade 1/2: 1 year off. Grade 3/4: 2 years off from completion of primary treatment."},
            "Multiple Sclerosis / MND": {"g1": "Pass test.", "g2": "Revoked.", "notif": "Yes", "ref": "Must notify. Driving may continue if no sudden disabling symptoms or significant cognitive impairment."},
            "Dementia": {"g1": "Cognition dependent.", "g2": "Revoked.", "notif": "Yes", "ref": "Licence may be granted subject to annual medical review and/or on-road driving assessment."},
            "Parkinson's Disease": {"g1": "Pass test.", "g2": "Revoked.", "notif": "Yes", "ref": "Must notify. Licensing depends on maintaining safe control and absence of significant motor/cognitive fluctuations."}
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI / ACS (STEMI/NSTEMI)": {"g1": "1-4 weeks off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week off if: Successful PCI, LVEF > 40%, and no other revascularisation planned. Otherwise, 4 weeks off."},
            "Angina (Symptomatic)": {"g1": "Stop until stable.", "g2": "Revoked.", "notif": "No (G1)", "ref": "Must not drive when symptoms occur at rest, with emotion, or at the wheel."},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "Must not drive for 1 week (G1) or 6 weeks (G2) following implantation or battery change."},
            "ICD (Prophylactic)": {"g1": "1 month off.", "g2": "Permanent bar.", "notif": "Yes", "ref": "Group 1: 1 month off if asymptomatic. Group 2: Permanent bar for any ICD implantation."},
            "ICD (Symptomatic/Sustained VT)": {"g1": "6 months off.", "g2": "Permanent bar.", "notif": "Yes", "ref": "Group 1: 6 months off from the date of the event or last shock."},
            "Heart Failure (NYHA IV)": {"g1": "Must not drive.", "g2": "Must not drive.", "notif": "Yes", "ref": "Driving is prohibited if symptoms occur at rest or minimal exertion."},
            "Aortic Aneurysm": {"g1": ">6.5cm Stop.", "g2": ">5.5cm Stop.", "notif": "Yes", "ref": "Group 1: Notify if >6cm. Disqualified if >6.5cm. Group 2: Disqualified if >5.5cm."},
            "Valvular Heart Disease": {"g1": "Stop until stable.", "g2": "Revoked.", "notif": "Yes", "ref": "Must notify and stop driving if symptoms (e.g. syncope, dyspnoea) are present."}
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Must test glucose <2 hours before driving and every 2 hours while driving. Adequate hypo awareness is mandatory."},
            "Severe Hypoglycaemia": {"g1": "12m off if 2+ events.", "g2": "12m off if 1 event.", "notif": "Yes", "ref": "Group 1: Revoked if 2 episodes of severe hypo (requiring third-party help) occur within 12 months."},
            "Hypoglycaemia Unawareness": {"g1": "Must not drive.", "g2": "Must not drive.", "notif": "Yes", "ref": "Must notify. Licence revoked until awareness is regained."},
            "Non-Insulin (Sulphonylureas)": {"g1": "No (unless hypos).", "g2": "Notify DVLA.", "notif": "G2 Yes / G1 No", "ref": "Group 2 must notify. Group 1 only if there have been severe hypoglycaemic events."}
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "3m stable.", "g2": "12m stable.", "notif": "Yes", "ref": "Must be stable for 3 months (G1) or 12 months (G2) on medication with no significant side effects."},
            "Bipolar Disorder": {"g1": "Stable 3m.", "g2": "Stable 12m.", "notif": "Yes", "ref": "Must notify. Driving prohibited during mania, hypomania, or severe depression."},
            "Severe Depression / Anxiety": {"g1": "Pass clinical.", "g2": "6m stability.", "notif": "Yes (if severe)", "ref": "Notify if concentration or suicidal ideation is present."}
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "Licence revoked until 1 year of abstinence or controlled drinking has been attained."},
            "Drug Misuse (Cannabis/Cocaine)": {"g1": "6-12m off.", "g2": "12m off.", "notif": "Yes", "ref": "Persistent misuse requires 6-12 months free of misuse (G1) and 1 year for G2."}
        }
    },
    "Chapter 6: Vision": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Visual Acuity Standard": {"g1": "6/12 and 20m plate.", "g2": "6/7.5 and 6/60.", "notif": "If standard not met", "ref": "Must read 79mm plate at 20m. Field of 120 degrees horizontal required for G1."},
            "Visual Field Defect": {"g1": "Must stop.", "g2": "Must stop.", "notif": "Yes", "ref": "Must notify. Most field defects (e.g. hemianopia) are a bar to driving unless a special test is passed."},
            "Diplopia": {"g1": "Stop until stable.", "g2": "Stop until stable.", "notif": "Yes", "ref": "Must not drive. May resume if controlled by a patch and meets acuity standards."}
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until controlled.", "g2": "Stop until controlled.", "notif": "Yes", "ref": "Must not drive if excessive sleepiness is present. May resume once CPAP control is confirmed."},
            "Chronic Renal Failure": {"g1": "Clinical discretion.", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "Group 1: No restriction unless symptomatic fatigue. Group 2: Must notify."}
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Post-Surgery (General)": {"g1": "1-3 months.", "g2": "Occ Health review.", "notif": "No (<3m)", "ref": "Notify only if restrictions exceed 3 months."},
            "Hepatic Encephalopathy": {"g1": "Must stop.", "g2": "Must stop.", "notif": "Yes", "ref": "Must not drive and must notify. May resume once treatment is successful and stable."}
        }
    }
}

# --- NAVIGATION ---
st.title("🩺 DVLA Clinical Standards Navigator")
c1, c2 = st.columns(2)
with c1:
    chap = st.selectbox("📁 System Chapter", options=list(DVLA_DATA.keys()))
with c2:
    cond = st.selectbox("🔬 Clinical Condition", options=list(DVLA_DATA[chap]["conditions"].keys()))

st.link_button(f"🔗 Source: {chap} (GOV.UK)", DVLA_DATA[chap]["url"])

# --- DATA RETRIEVAL ---
res = DVLA_DATA[chap]["conditions"][cond]

# --- SIDEBAR CALCULATOR (FIXED VISIBILITY) ---
with st.sidebar:
    st.header("⏳ Cessation Clock")
    evt_date = st.date_input("Date of Event:", value=date.today())
    unit = st.radio("Unit:", ["Weeks", "Months"], horizontal=True)
    num = st.number_input(f"Number of {unit}:", min_value=0, value=1)
    
    delta = timedelta(weeks=num) if unit == "Weeks" else timedelta(days=int(num * 30.44))
    resume = evt_date + delta
    st.metric("Resume Date", resume.strftime('%d/%m/%Y'))

# --- MAIN CLINICAL VERDICT ---
st.divider()
col_notif, col_g1, col_g2 = st.columns([1, 1.5, 1.5])

with col_notif:
    notif_color = "#d32f2f" if "yes" in res['notif'].lower() else "#2e7d32"
    st.markdown(f"**🔔 Notifiable?**\n\n<span style='color:{notif_color}; font-size: 1.25em; font-weight: bold;'>{res['notif']}</span>", unsafe_allow_html=True)

with col_g1:
    st.info(f"**🚗 Group 1 (Car/Bike)**\n\n{res['g1']}")

with col_g2:
    st.warning(f"**🚛 Group 2 (HGV/Bus)**\n\n{res['g2']}")

# --- OFFICIAL REFERENCE ---
st.divider()
st.subheader("📖 Official Regulatory Reference")
st.markdown(f'<div class="ref-box">{res["ref"]}</div>', unsafe_allow_html=True)

# --- MEDICAL NOTE ---
st.divider()
st.subheader("🖋️ Proposed Medical Entry")
st.code(f"DVLA FITNESS TO DRIVE: Discussed {cond}. Guidance ref: '{res['ref']}'. Advised {num} {unit.lower()} cessation from {evt_date.strftime('%d/%m/%Y')}. Earliest resume date: {resume.strftime('%d/%m/%Y')}. Notifiable to DVLA: {res['notif']}.", language="text")
