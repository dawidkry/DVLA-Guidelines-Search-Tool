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

# --- MAXIMIZED CLINICAL DATABASE ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. Resume after 1 month if no residual deficit. Notify only if deficit persists."},
            "Epilepsy (Isolated Seizure)": {"g1": "6-12 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months off if scans/EEG clear. 12 months if underlying risk/lesion."},
            "Subarachnoid Haemorrhage": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if no intervention or successful coiling with no deficit."},
            "Chronic Subdural": {"g1": "6 months off.", "g2": "6 months off.", "notif": "Yes", "ref": "6 months from the date of the event/surgery."},
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "ACS (PCI performed)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no other planned procedures."},
            "Aortic Aneurysm (>6cm)": {"g1": "Notify/Stop.", "g2": "Disqualified.", "notif": "Yes", "ref": "G1: Notify if >6cm. Disqualified if >6.5cm. G2: Disqualified if >5.5cm."},
            "Marfan Syndrome (Aorta)": {"g1": "Discretion/Notify.", "g2": "Revoked.", "notif": "Yes", "ref": "G2: Prohibited if aortic root >50mm."},
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "1 year abstinence or controlled drinking (G1). G2 requires 3 years."},
            "Alcohol Misuse": {"g1": "6 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Clinical freedom from misuse for specified period."},
            "Cannabis Misuse": {"g1": "6 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Persistent misuse: 6 months (G1) or 1 year (G2) free of use."},
            "Cocaine / Meth Misuse": {"g1": "1 year off.", "g2": "1 year off.", "notif": "Yes", "ref": "Persistent misuse or dependence requires 1 year clean of misuse."},
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Visual Acuity (Failed)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must read 79mm plate at 20m. Must reach 6/12 on Snellen chart."},
            "Hemianopia (Complete)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Exceptional cases (G1) may apply for an on-road test after 12 months stability."},
            "Quadrantanopia": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must notify. Requires Esterman field test to assess binocular field of 120 degrees."},
            "Monocularity (New)": {"g1": "Adaptation period.", "g2": "Notify/Stop.", "notif": "G2 Yes", "ref": "G1: No formal period but must ensure adaptation and meet field standards."},
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (Suspected)": {"g1": "Drive (unless sleepy).", "g2": "Drive (unless sleepy).", "notif": "No", "ref": "Only notify if excessive sleepiness occurs at appropriate times."},
            "Sleep Apnoea (Diagnosed)": {"g1": "Stop until CPAP.", "g2": "Stop until CPAP.", "notif": "Yes", "ref": "Notify DVLA. Resume only when CPAP control is medically confirmed."},
            "Cough Syncope": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months off from the last episode. G2 is 5 years off."},
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Post-Surgery (Abdominal)": {"g1": "Discretion.", "g2": "Clinical Review.", "notif": "No", "ref": "G1: Resume when able to perform emergency stop and pain-free. Usually 4-6 weeks."},
            "Post-Surgery (Neurosurgery)": {"g1": "6-12 months.", "g2": "Revoked.", "notif": "Yes", "ref": "Depends on the underlying pathology and presence of seizures."},
            "Medication (Opiates)": {"g1": "Patient Duty.", "g2": "Patient Duty.", "notif": "No", "ref": "Illegal to drive if impaired. Advise patients on sedative effects of chronic analgesia."},
            "Cognitive Decline": {"g1": "On-road test.", "g2": "Revoked.", "notif": "Yes", "ref": "Notify DVLA. Usually involves a formal driving assessment if diagnosis is uncertain."},
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
st.code(f"DVLA FITNESS TO DRIVE ASSESSMENT:\nClinical Context: {cond}\nRegulatory Guidance: {res['ref']}\nAdvice: Cease driving for {num} {unit.lower()} from {evt_date.strftime('%d/%m/%Y')}.\nEarliest Potential Resume: {resume.strftime('%d/%m/%Y')}\nDVLA Notification Required: {res['notif']}.", language="text")
