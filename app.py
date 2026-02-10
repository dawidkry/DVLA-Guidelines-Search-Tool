import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards 2026", page_icon="🩺", layout="wide")

# --- STYLING (BLACK SIDEBAR / WHITE TEXT) ---
st.markdown("""
    <style>
    /* 1. Sidebar: Solid Black Background */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }
    
    /* 2. Sidebar Text: Pure White */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2 {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    
    /* 3. Sidebar Inputs: White Background, Black Text (for usability) */
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 4. Sidebar Metric (Resume Date): High Contrast White */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 2rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #BBBBBB !important;
    }

    /* 5. Reference Box (Main Page) */
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
            "TIA / Stroke": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. May resume after 1 month if no residual deficit. Notify DVLA only if residual neurological deficit persists."},
            "Syncope (Simple Vasovagal)": {"g1": "No restriction.", "g2": "No restriction.", "notif": "No", "ref": "No restriction if there is a clear prodrome and the event occurred while standing/sitting. Prohibited if occurred while driving."},
            "Syncope (Unexplained TLoC)": {"g1": "6-12 months off.", "g2": "12 months off.", "notif": "Yes", "ref": "Unexplained syncope: 6 months off (G1) or 12 months if high-risk features present."},
            "Epilepsy (First Seizure)": {"g1": "6-12 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months off if scans/EEG are clear. 12 months off if there is an underlying risk or brain lesion."},
            "Parkinson's Disease": {"g1": "Pass test.", "g2": "Revoked.", "notif": "Yes", "ref": "Licence depends on maintaining safe control and absence of significant motor/cognitive fluctuations."}
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI / ACS (STEMI/NSTEMI)": {"g1": "1-4 weeks off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week off if: Successful PCI, LVEF > 40%, and no other revascularisation planned. Otherwise, 4 weeks off."},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "Must not drive for 1 week (G1) or 6 weeks (G2) following implantation or battery change."},
            "Aortic Aneurysm": {"g1": ">6.5cm Stop.", "g2": ">5.5cm Stop.", "notif": "Yes", "ref": "Group 1: Notify if >6cm. Disqualified if >6.5cm. Group 2: Disqualified if >5.5cm."}
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Must test glucose <2 hours before driving and every 2 hours while driving."},
            "Severe Hypoglycaemia": {"g1": "12m off if 2+ events.", "g2": "12m off if 1 event.", "notif": "Yes", "ref": "Group 1: Revoked if 2 episodes of severe hypo (requiring third-party help) occur within 12 months."}
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "3m stable.", "g2": "12m stable.", "notif": "Yes", "ref": "Must be stable for 3 months (G1) or 12 months (G2) on medication."}
        }
    },
    "Chapter 6: Vision": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Visual Acuity Standard": {"g1": "6/12 and 20m plate.", "g2": "6/7.5 and 6/60.", "notif": "If standard not met", "ref": "Must read 79mm plate at 20m. Field of 120 degrees horizontal required for G1."}
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

# --- DATA ---
res = DVLA_DATA[chap]["conditions"][cond]

# --- SIDEBAR (BLACK BACKGROUND) ---
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
