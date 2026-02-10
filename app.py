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

# --- THE FULL 8-CHAPTER CLINICAL DATABASE ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. Resume after 1 month if no residual deficit. Notify only if deficit persists."},
            "Epilepsy (Isolated Seizure)": {"g1": "6-12 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months off if scans/EEG clear. 12 months if underlying risk/lesion."},
            "Parkinson's Disease": {"g1": "Pass medical.", "g2": "Revoked.", "notif": "Yes", "ref": "Must notify. Licensing depends on maintaining safe control and absence of significant motor/cognitive fluctuations."},
            "Multiple Sclerosis / MND": {"g1": "Pass medical.", "g2": "Revoked.", "notif": "Yes", "ref": "Must notify. Prohibited if sudden disabling symptoms occur."},
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "ACS (PCI performed)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no other planned procedures."},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "Includes new implants and battery/box changes."},
            "ICD (Symptomatic/Shocked)": {"g1": "6 months off.", "g2": "Permanent bar.", "notif": "Yes", "ref": "6 months off from the date of the event or last shock."},
            "Aortic Aneurysm (>6.5cm)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "G1 disqualified if >6.5cm. G2 disqualified if >5.5cm."},
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Must test glucose <2h before driving and every 2h while driving. Adequate hypo awareness is mandatory."},
            "Severe Hypoglycaemia (G1)": {"g1": "12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "Revoked if 2 episodes of severe hypo (requiring help) occur in 12 months."},
            "Severe Hypoglycaemia (G2)": {"g1": "Discretion.", "g2": "12 months off.", "notif": "Yes", "ref": "Group 2 revoked for 12 months following a single episode of severe hypo."},
            "Hypoglycaemia Unawareness": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must notify. License revoked until awareness is regained to specialist satisfaction."},
            "Sulfonylurea Treated": {"g1": "No (unless hypos).", "g2": "Notify DVLA.", "notif": "G2 Yes / G1 No", "ref": "G2 must notify. G1 only if there have been severe hypoglycaemic events."},
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Must be stable on medication, compliant, and free from significant side effects."},
            "Hypomania / Mania": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "License revoked during acute episodes. Must notify and be stable for specified period."},
            "Severe Depression / Anxiety": {"g1": "Pass clinical.", "g2": "6 months stable.", "notif": "Only if severe", "ref": "Notify only if concentration, agitation, or suicidal ideation is present."},
            "Personality Disorder": {"g1": "Clinical discretion.", "g2": "Revoked (if severe).", "notif": "Yes", "ref": "Notify if the condition is likely to cause a medical risk to road safety."},
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "Requires 1 year (G1) or 3 years (G2) of abstinence or controlled drinking."},
            "Cannabis Misuse": {"g1": "6 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Persistent misuse: 6 months (G1) or 1 year (G2) free of use."},
            "Cocaine / Meth Misuse": {"g1": "1 year off.", "g2": "1 year off.", "notif": "Yes", "ref": "Requires 1 year free of misuse and clinical stability."},
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Visual Acuity Standard": {"g1": "6/12 and 20m plate.", "g2": "6/7.5 and 6/60.", "notif": "No (if met)", "ref": "Must read 79mm plate at 20m. Field of 120 degrees horizontal required for G1."},
            "Visual Field Defect": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Includes hemianopia and quadrantanopia. Requires Esterman field test for appeal."},
            "Diplopia": {"g1": "Stop until stable.", "g2": "Stop until stable.", "notif": "Yes", "ref": "May resume if controlled by a patch/prisms and meet acuity standards."},
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP.", "g2": "Stop until CPAP.", "notif": "Yes", "ref": "Must not drive if excessive sleepiness. Resume once CPAP control is confirmed."},
            "Cough Syncope": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months off from the last episode. Group 2 is 5 years off."},
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Post-Surgery (Abdominal)": {"g1": "Discretion.", "g2": "Clinical Review.", "notif": "No", "ref": "Resume when able to perform emergency stop and pain-free (approx 4-6 weeks)."},
            "Age (70+)": {"g1": "3-year renewal.", "g2": "Annual medical.", "notif": "Renewal req", "ref": "Licences must be renewed every 3 years from age 70 for Group 1."},
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
