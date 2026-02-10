import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Navigator 2026", page_icon="🩺", layout="wide")

# --- COMPREHENSIVE DATASET WITH EXACT PARAGRAPHS ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {
                "g1": "1 month off. Resume if no residual deficit.",
                "g2": "1 year off. Requires stable imaging.",
                "notif": "No (G1)",
                "ref_para": "Must not drive for at least 1 month. May resume only after a clinical recovery is satisfactory. There is no need to notify DVLA unless there is residual neurological deficit 1 month after the episode (e.g. visual field defects, cognitive defects, or impaired limb function)."
            },
            "Syncope (Simple Vasovagal)": {
                "g1": "No restriction.",
                "g2": "No restriction.",
                "notif": "No",
                "ref_para": "Simple vasovagal faint: No restriction on driving and no need to notify the DVLA. This applies to faints occurring while standing or sitting, provided there is a clear prodrome and avoidable trigger."
            },
            "Syncope (Unexplained TLoC)": {
                "g1": "6 months off (low risk) or 12 months (high risk).",
                "notif": "Yes",
                "ref_para": "Unexplained syncope: Must stop driving and notify the DVLA. If no cause is identified, the licence will be refused or revoked for 6 months (Group 1) or 12 months if there are high-risk features."
            },
            "Epilepsy (First Seizure)": {
                "g1": "6 or 12 months off.",
                "notif": "Yes",
                "ref_para": "First unprovoked epileptic seizure: Must not drive and must notify DVLA. Driving must cease for 6 months from the date of the seizure, or for 12 months if there is an underlying causative factor that may increase risk."
            }
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI (ACS)": {
                "g1": "1 week (if PCI) else 4 weeks.",
                "notif": "No (G1)",
                "ref_para": "Acute coronary syndrome (ACS): Driving may resume 1 week after ACS if successful coronary intervention (PCI) has been carried out, LV ejection fraction is at least 40%, and no other urgent revascularisation is planned. Otherwise, 4 weeks off."
            },
            "Pacemaker Insertion": {
                "g1": "1 week off.",
                "notif": "Yes",
                "ref_para": "Pacemaker implantation: Must not drive for at least 1 week and must notify the DVLA. This includes battery/box changes."
            }
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {
                "g1": "1-3 year licence. Must check glucose.",
                "notif": "Yes",
                "ref_para": "Insulin-treated drivers: Must notify DVLA. Must practice blood glucose monitoring (no more than 2 hours before start of journey and every 2 hours while driving). Must not have more than one episode of severe hypoglycaemia in the last 12 months."
            }
        }
    }
}

# --- STYLING ---
st.markdown("""
    <style>
    .ref-box {
        background-color: #f0f2f6;
        border-left: 5px solid #005eb8;
        padding: 15px;
        border-radius: 5px;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
st.title("🩺 DVLA Clinical Reference Tool")

col_chap, col_cond = st.columns(2)
with col_chap:
    chap_name = st.selectbox("📁 Select Chapter", options=list(DVLA_DATA.keys()), key="c_sel")
with col_cond:
    cond_name = st.selectbox("🔬 Select Condition", options=list(DVLA_DATA[chap_name]["conditions"].keys()), key="n_sel")

# --- DATA RETRIEVAL ---
res = DVLA_DATA[chap_name]["conditions"][cond_name]

# --- MAIN DISPLAY ---
st.divider()

c1, c2 = st.columns([2, 1])

with c1:
    st.subheader(f"Recommendations: {cond_name}")
    st.info(f"**🚗 Group 1 (Car/Bike):** {res['g1']}")
    st.warning(f"**🚛 Group 2 (HGV/Bus):** {res.get('g2', 'Refer to full guidance')}")
    st.error(f"**🔔 Notification Required:** {res['notif']}")

with c2:
    st.header("⏳ Calculator")
    event_date = st.date_input("Event Date:", value=date.today())
    unit = st.radio("Unit:", ["Weeks", "Months"], horizontal=True)
    num = st.number_input("Duration:", min_value=0, value=1)
    
    delta = timedelta(weeks=num) if unit == "Weeks" else timedelta(days=int(num * 30.44))
    resume = event_date + delta
    st.metric("Resume Date", resume.strftime('%d/%m/%Y'))

# --- THE "EXACT PARAGRAPH" SECTION ---
st.divider()
st.subheader("📖 Official Guidance Text (Reference)")
st.markdown(f'<div class="ref-box">{res["ref_para"]}</div>', unsafe_allow_html=True)

# --- CLINICAL NOTE ---
st.divider()
st.subheader("🖋️ Proposed Medical Entry")
note = f"DVLA ADVICE: Discussed {cond_name}. Official guidance states: '{res['ref_para']}'. Advised {num} {unit.lower()} cessation from {event_date.strftime('%d/%m/%Y')}. Notify DVLA: {res['notif']}."
st.code(note, language="text")
