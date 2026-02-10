import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Navigator 2026", page_icon="🩺", layout="wide")

# --- THE MEGA DATASET ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {
                "g1": "1 month off.", "g2": "1 year off.", "notif": "No (unless residual deficit)",
                "ref": "MUST NOT DRIVE for 1 month. May resume after 1 month if no residual deficit. Notify DVLA only if residual neurological deficit persists (e.g., visual field, cognition, limb function)."
            },
            "Syncope (Simple Vasovagal)": {
                "g1": "No restriction.", "g2": "No restriction.", "notif": "No",
                "ref": "No restriction if there is a clear prodrome and the event occurred while standing or sitting. Must not drive if it occurred while driving or with no prodrome."
            },
            "Syncope (Unexplained TLoC)": {
                "g1": "6-12 months off.", "g2": "12 months off.", "notif": "Yes",
                "ref": "If no cause identified: 6 months off (Group 1) or 12 months off if high-risk features present. Group 2 is usually 12 months off."
            },
            "Cough Syncope": {
                "g1": "Stop until controlled.", "g2": "Revoked until 3m clear.", "notif": "Yes",
                "ref": "Must stop driving. May resume only when the condition is controlled and the risk of recurrence is low. Notification is mandatory."
            },
            "Epilepsy (First Seizure)": {
                "g1": "6-12 months off.", "g2": "5 years off.", "notif": "Yes",
                "ref": "Standard unprovoked seizure: 6 months off if scans are clear. 12 months off if there is an underlying risk/lesion."
            },
            "Brain Tumour (Malignant)": { "g1": "1-2 years off.", "g2": "Permanent bar.", "notif": "Yes", "ref": "Dependent on WHO Grade. Grade 1/2 often 1 year; Grade 3/4 often 2 years off." },
            "Subarachnoid Haemorrhage": { "g1": "6 months off.", "g2": "Dependent on repair.", "notif": "Yes", "ref": "6 months off for Group 1 if no intervention or successful coiling/clipping." },
            "Dementia": { "g1": "Mild: Pass test.", "g2": "Revoked.", "notif": "Yes", "ref": "Must notify. Licence may be granted subject to annual medical review and/or on-road driving assessment." }
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI / ACS (STEMI/NSTEMI)": {
                "g1": "1-4 weeks off.", "g2": "6 weeks off.", "notif": "No (G1)",
                "ref": "1 week off if: Successful PCI, LVEF > 40%, and no other planned revascularisation. Otherwise, 4 weeks off."
            },
            "Pacemaker Insertion": { "g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "Must not drive for 1 week (G1) or 6 weeks (G2) following implantation or box change." },
            "Angina (Symptomatic)": { "g1": "Stop when symptoms occur.", "g2": "Revoked.", "notif": "No (G1)", "ref": "Must not drive when symptoms occur at the rest or at the wheel." },
            "Atrial Fibrillation": { "g1": "No restriction.", "g2": "Symptom dependent.", "notif": "No", "ref": "May drive if no symptoms likely to cause incapacity or distraction." },
            "Aortic Aneurysm": { "g1": ">6.5cm Stop.", "g2": ">5.5cm Stop.", "notif": "Yes", "ref": "Group 1: Notify if >6cm. Disqualified if >6.5cm. Group 2: Disqualified if >5.5cm." },
            "Heart Failure (NYHA IV)": { "g1": "Must not drive.", "g2": "Must not drive.", "notif": "Yes", "ref": "Driving is prohibited if symptoms occur at rest or minimal exertion." }
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": { "g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Must have 'adequate' hypo awareness. Must test glucose <2 hours before driving and every 2 hours while driving." },
            "Severe Hypoglycaemia": { "g1": "12m off if 2+ events.", "g2": "12m off if 1 event.", "notif": "Yes", "ref": "Group 1: Revoked if 2 episodes of severe hypo (requiring help) occur within 12 months." }
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": { "g1": "3m stable.", "g2": "12m stable.", "notif": "Yes", "ref": "Must not drive during acute phase. Must be stable for 3 months (G1) or 12 months (G2) on meds with no significant side effects." },
            "Bipolar Disorder": { "g1": "Stable 3m.", "g2": "Stable 6-12m.", "notif": "Yes", "ref": "Must notify. Driving prohibited during mania or severe depression." }
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": { "g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "Licence revoked until 1 year of abstinence or controlled drinking has been attained." },
            "Drug Misuse (Cannabis/Cocaine)": { "g1": "6m-1yr off.", "g2": "1yr off.", "notif": "Yes", "ref": "Persistent misuse requires a period of 6-12 months free of misuse before relicensing." }
        }
    },
    "Chapter 6: Vision": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Visual Acuity (6/12)": { "g1": "Standard 6/12.", "g2": "Standard 6/7.5.", "notif": "If standard not met", "ref": "Must be able to read in good light a registration mark fixed to a motor vehicle and containing letters and figures 79mm high and 50mm wide at a distance of 20 metres." },
            "Diplopia": { "g1": "Stop until stable.", "g2": "Stop until stable.", "notif": "Yes", "ref": "Must not drive. Driving may resume if the diplopia is controlled (e.g. by a patch) and the vision meets the required standards." }
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": { "g1": "Stop until controlled.", "g2": "Stop until controlled.", "notif": "Yes", "ref": "Must not drive if excessive sleepiness is present. Must notify DVLA. May resume once control is confirmed by a specialist." }
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Post-Surgery": { "g1": "Clinical discretion.", "g2": "Clinical discretion.", "notif": "No (<3m)", "ref": "Drivers do not need to notify the DVLA unless medical restrictions are likely to last more than 3 months." }
        }
    }
}

# --- STYLING ---
st.markdown("""
    <style>
    .ref-box {
        background-color: #ffffff;
        color: #1e1e1e;
        padding: 20px;
        border: 2px solid #005eb8;
        border-radius: 8px;
        font-size: 1.1em;
        line-height: 1.5;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stSelectbox label { color: #005eb8; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- NAV ---
st.title("🩺 DVLA Clinical Standards Navigator (Full Edition)")
st.caption("A peer-to-peer tool for medical professionals.")

c1, c2 = st.columns(2)
with c1:
    chap = st.selectbox("📁 System Chapter", options=list(DVLA_DATA.keys()))
with c2:
    cond = st.selectbox("🔬 Clinical Condition", options=list(DVLA_DATA[chap]["conditions"].keys()))

st.link_button(f"🔗 Open Official {chap} (Live Page)", DVLA_DATA[chap]["url"])

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
    st.divider()
    st.write(f"**Notifiable:** {res['notif']}")

# --- MAIN DISPLAY ---
st.divider()
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.info(f"**🚗 Group 1 (Car/Bike)**\n\n{res['g1']}")
with col_g2:
    st.warning(f"**🚛 Group 2 (HGV/Bus)**\n\n{res['g2']}")

# --- LEGIBLE OFFICIAL GUIDANCE ---
st.subheader("📖 Official Regulatory Text")
st.markdown(f'<div class="ref-box">{res["ref"]}</div>', unsafe_allow_html=True)

# --- MEDICAL NOTE ---
st.divider()
st.subheader("🖋️ Discharge Note / Clinical Entry")
st.code(f"DVLA FITNESS TO DRIVE: Discussed {cond}. Official advice: '{res['ref']}'. Advised {num} {unit.lower()} cessation from {evt_date.strftime('%d/%m/%Y')}. Notify DVLA: {res['notif']}.", language="text")
