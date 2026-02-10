import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards 2026", page_icon="🩺", layout="wide")

# --- UI CLEANUP, STATIC SIDEBAR & STYLING ---
st.markdown("""
    <style>
    /* 1. HIDE ALL TOOLBARS AND BUTTONS */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stToolbar"] {display:none !important;}

    /* 2. MAKE SIDEBAR STATIC (Hide Toggle Button) */
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* 3. SIDEBAR: SOLID BLACK BACKGROUND */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        min-width: 300px !important;
        max-width: 300px !important;
    }
    
    /* 4. SIDEBAR TEXT: WHITE */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] li {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    
    /* 5. SIDEBAR INPUTS: CONTRAST FIX */
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 6. METRICS & DISCLAIMER */
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

# --- MAXIMIZED CLINICAL DATABASE (ALL 8 CHAPTERS) ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke (Single)": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. Resume after 1 month if no residual deficit."},
            "TIA / Stroke (Multiple/Recurrent)": {"g1": "3 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Recurrent events within short period require 3 months cessation for Group 1."},
            "Epilepsy (Unprovoked)": {"g1": "6-12 months off.", "g2": "10 years off.", "notif": "Yes", "ref": "Standard 12 months. 6 months if low risk (<2% recurrence/year). G2 10 years free of meds."},
            "Seizure (Provoked - e.g. ETOH Withdrawal)": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Provoked by acute factor. 6 months if clinical risk is low."},
            "Meningioma (Benign)": {"g1": "6-12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months off if treated by surgery with no seizure or deficit."},
            "Pituitary Tumour": {"g1": "Resume when stable.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Licensing depends on visual field results (Esterman test)."},
            "Narcolepsy / Cataplexy": {"g1": "Stop driving.", "g2": "Revoked.", "notif": "Yes", "ref": "Must stop driving until symptoms controlled and specialist satisfaction confirmed."},
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "ACS (PCI performed)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no other planned procedures."},
            "ACS (Medical Management)": {"g1": "4 weeks off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "4 weeks mandatory cessation for Group 1."},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "1 week (G1) or 6 weeks (G2) following surgery/battery change."},
            "Hypertrophic Cardiomyopathy (HCM)": {"g1": "Drive (unless high risk).", "g2": "Notify/Review.", "notif": "G2 Yes", "ref": "G2 drivers barred if annual risk of sudden event >2%."},
            "Brugada Syndrome (Asymptomatic)": {"g1": "No restriction.", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "G2 requires specialist report confirming low risk."},
            "Aneurysm (5.5cm - 5.9cm)": {"g1": "Drive (Notify).", "g2": "Disqualified.", "notif": "Yes", "ref": "G2 disqualified if >5.5cm. G1 notify if >6.0cm."},
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin (Standard)": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Monitor glucose <2h before driving and every 2h while driving."},
            "Severe Hypoglycaemia (x2 in 12m)": {"g1": "12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "G1 revoked if 2 episodes requiring help occur in 1 year."},
            "Hypo Unawareness (Complete)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must regain awareness before license reinstatement."},
            "Metformin Only": {"g1": "No notification.", "g2": "No notification.", "notif": "No", "ref": "Provided no severe hypos occur and standard vision met."},
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Schizophrenia / Psychosis": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Must be free from significant side effects of antipsychotics."},
            "Bipolar (Acute Episode)": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Stability period starts from date of resolution of mania/depression."},
            "Personality Disorder (Severe)": {"g1": "Clinical Discretion.", "g2": "Revoked.", "notif": "Yes", "ref": "Notify if behaviors likely to affect road safety (e.g., aggression)."},
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "1 year (G1) or 3 years (G2) abstinence or controlled drinking."},
            "Cannabis Misuse (Persistent)": {"g1": "6 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Clinical freedom from misuse for specified period."},
            "Cocaine / Amphetamines": {"g1": "1 year off.", "g2": "1 year off.", "notif": "Yes", "ref": "Standard 1 year cessation for stimulant misuse."},
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Acuity Failure": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must read 79mm plate at 20m. Must reach 6/12 (G1) or 6/7.5 (G2)."},
            "Glaucoma (Advanced)": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Requires Esterman visual field test. Licensing depends on binocular field."},
            "Diplopia": {"g1": "Stop until stable.", "g2": "Stop until stable.", "notif": "Yes", "ref": "May resume if controlled by patch or prisms."},
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP.", "g2": "Stop until CPAP.", "notif": "Yes", "ref": "Notify DVLA. Resume when sleepiness controlled by CPAP."},
            "Cough Syncope (Single)": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "G1: 6 months. G2: 5 years cessation from last event."},
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Age 70+": {"g1": "3yr renewal.", "g2": "N/A", "notif": "Yes", "ref": "Group 1 must renew license every 3 years from age 70."},
            "Post-Op (General Surgery)": {"g1": "4-6 weeks off.", "g2": "Clinical Review.", "notif": "No", "ref": "Resume when able to perform emergency stop safely and pain-free."},
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

# --- STATIC SIDEBAR ---
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
