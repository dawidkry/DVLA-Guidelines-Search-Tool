import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards 2026", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

# --- UI STYLING (FIXED SIDEBAR VISIBILITY) ---
st.markdown("""
    <style>
    /* 1. HIDE TOOLBARS */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display:none !important;}

    /* 2. SIDEBAR STYLING: SOLID BLACK & FORCED VISIBLE */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        width: 350px !important;
    }
    
    /* 3. SIDEBAR TEXT: WHITE */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] span {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    
    /* 4. SIDEBAR INPUTS */
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 5. CLINICAL VERDICT BOXES */
    .ref-box {
        background-color: #f8f9fa; color: #1a1a1a; padding: 20px;
        border-left: 5px solid #005eb8; border-radius: 4px; font-size: 1.05em;
    }
    .disclaimer-sidebar {
        background-color: #440000; color: #FFCCCC; padding: 12px;
        border-radius: 5px; border: 1px solid #FF0000; font-size: 0.9em; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- THE ABSOLUTE CLINICAL DATABASE ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke (Single)": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. Resume after 1 month if no residual deficit."},
            "TIA / Stroke (Multiple/Recurrent)": {"g1": "3 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Recurrent events require 3 months cessation for Group 1."},
            "Epilepsy (Unprovoked Seizure)": {"g1": "12 months off.", "g2": "10 years off.", "notif": "Yes", "ref": "12 months standard. 6 months if low risk (<2% per annum)."},
            "Epilepsy (Sleep-only Pattern)": {"g1": "1-3 years off.", "g2": "Revoked.", "notif": "Yes", "ref": "Can drive after 1 year if established sleep-only pattern; otherwise 3 years."},
            "Provoked Seizure (Acute Head Injury)": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Seizure occurring within 24 hours of a TBI or acute insult."},
            "Meningioma (Benign)": {"g1": "6-12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if treated by surgery with no seizure or deficit."},
            "Glioblastoma / Malignant Tumour": {"g1": "2 years off.", "g2": "Revoked.", "notif": "Yes", "ref": "2 years off following completion of primary treatment."},
            "Dementia (Mild/Moderate)": {"g1": "Notify/Review.", "g2": "Revoked.", "notif": "Yes", "ref": "Licensing depends on on-road assessment and cognitive testing (e.g., MMSE/MoCA)."},
            "Multiple Sclerosis": {"g1": "Notify DVLA.", "g2": "Revoked.", "notif": "Yes", "ref": "Must notify. Focus on visual fields and sudden disabling symptoms."},
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "ACS (PCI performed)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no other planned procedures."},
            "ACS (No PCI - Medical Mgmt)": {"g1": "4 weeks off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "4 weeks cessation for Group 1 car/bike drivers."},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "1 week (G1) or 6 weeks (G2) following surgery/battery change."},
            "ICD (Symptomatic)": {"g1": "6 months off.", "g2": "Permanent Bar.", "notif": "Yes", "ref": "6 months from last shock. G2 is permanently disqualified."},
            "Aortic Aneurysm (6.0-6.4cm)": {"g1": "Notify/Drive.", "g2": "Stop driving.", "notif": "Yes", "ref": "G1 notify if >6.0cm. G2 disqualified if >5.5cm."},
            "Heart Failure (NYHA IV)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must not drive if symptoms occur at rest or minimal exertion."},
            "Hypertrophic Cardiomyopathy": {"g1": "Drive (usually).", "g2": "Revoked (if high risk).", "notif": "G2 Yes", "ref": "G2 barred if annual risk of sudden cardiac death >2%."},
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Test glucose <2h before driving and every 2h while driving."},
            "Severe Hypoglycaemia (Group 1)": {"g1": "12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "Revoked if 2 episodes of severe hypo (requiring help) in 1 year."},
            "Severe Hypoglycaemia (Group 2)": {"g1": "Discretion.", "g2": "12 months off.", "notif": "Yes", "ref": "Single episode of severe hypo while awake is a 12-month ban for G2."},
            "Hypo Unawareness": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must regain awareness before license reinstatement."},
            "Oral Medication (Gliclazide)": {"g1": "No notification.", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "G1 only if severe hypos occur. G2 must notify for all Sulphonylureas."},
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Schizophrenia / Psychosis": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Must be compliant and free from adverse med side effects."},
            "Mania / Bipolar": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Stable period from resolution of the acute episode."},
            "Severe Depression": {"g1": "Clinical Pass.", "g2": "6 months stable.", "notif": "If severe", "ref": "Notify if affects concentration or involves suicidal ideation."},
            "Personality Disorder": {"g1": "Discretion.", "g2": "Revoked.", "notif": "Yes", "ref": "Notify if behavioral symptoms (e.g. impulsivity) affect road safety."},
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "Requires abstinence or controlled drinking (G1=1yr, G2=3yrs)."},
            "Cannabis Misuse": {"g1": "6 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Clinical freedom from misuse for specified period."},
            "Cocaine / Stimulants": {"g1": "1 year off.", "g2": "1 year off.", "notif": "Yes", "ref": "Requires 1 year free of misuse and clinical stability."},
            "Opiate Dependence (Methadone)": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "G1 possible if stable on treatment with no misuse."},
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Acuity Standard": {"g1": "6/12 + 20m plate.", "g2": "6/7.5 + 6/60.", "notif": "No (if met)", "ref": "Must read 79mm plate at 20m. Horizontal field 120 deg required."},
            "Visual Field Defect (Hemianopia)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Exceptions possible for G1 after 1 year of adaptation and clinical review."},
            "Glaucoma (Advanced)": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Acuity and Esterman field test required."},
            "Diplopia": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "May resume if controlled by a patch or prisms."},
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP.", "g2": "Stop until CPAP.", "notif": "Yes", "ref": "Notify DVLA. Resume once control confirmed by specialist."},
            "Cough Syncope": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months (G1) or 5 years (G2) from the last event."},
            "Renal Failure (Dialysis)": {"g1": "No notification.", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "G2 drivers subject to medical report/review."},
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "General Surgery (Abdominal)": {"g1": "4-6 weeks.", "g2": "Review.", "notif": "No", "ref": "Resume when emergency stop is possible and pain-free."},
            "Age 70+ (Group 1)": {"g1": "3yr renewal.", "g2": "N/A.", "notif": "Yes", "ref": "Group 1 must renew license every 3 years from age 70."},
            "Syncope (Unexplained TLoC)": {"g1": "6-12 months.", "g2": "12 months.", "notif": "Yes", "ref": "6 months if low risk; 12 months if high risk or recurrent."},
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

# --- THE STATIC SIDEBAR (BLACK UI) ---
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
    st.markdown("- [DVLA Professional Index](https://www.gov.uk/guidance/assessing-fitness-to-drive-a-guide-for-medical-professionals)")
    
    st.markdown("""
        <div class="disclaimer-sidebar">
            <strong>⚠️ CLINICAL DISCLAIMER</strong><br>
            Decision-support only. Standards change. 
            <strong>Always verify</strong> latest guidance on GOV.UK.
        </div>
    """, unsafe_allow_html=True)

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
st.code(f"DVLA FITNESS TO DRIVE ASSESSMENT:\nClinical Context: {cond}\nRegulatory Guidance: {res['ref']}\nAdvice: Cease driving for {num} {unit.lower()} from {evt_date.strftime('%d/%m/%Y')}.\nEarliest Potential Resume: {resume.strftime('%d/%m/%Y')}\nDVLA Notification Required: {res['notif']}.", language="text")
