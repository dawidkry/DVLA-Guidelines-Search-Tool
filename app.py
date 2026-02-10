import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Standards 2026",
    page_icon="🩺",
    layout="wide"
)

# --- DATASET WITH HIGHLIGHTED DEEP LINKS ---
# We use #:~:text= to highlight the specific rule in the browser
DVLA_GUIDELINES = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {
                "g1": "1 month off. Resume if no residual deficit.", 
                "g2": "1 year off. Requires stable imaging.", 
                "notif": "No (unless residual deficit)",
                "link": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive#:~:text=Must%20not%20drive%20for%20at%20least%201%20month"
            },
            "Syncope (Simple Vasovagal)": {
                "g1": "No restriction if prodrome present.", 
                "g2": "No restriction unless occurring while sitting/standing.", 
                "notif": "No",
                "link": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive#:~:text=Simple%20vasovagal%20faint"
            },
            "Syncope (Unexplained TLoC)": {
                "g1": "6 months off (low risk) or 12 months (high risk).", 
                "g2": "12 months off minimum.", 
                "notif": "Yes",
                "link": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive#:~:text=Unexplained%20syncope"
            },
            "Epilepsy (First Seizure)": {
                "g1": "6 or 12 months off (specialist review).", 
                "g2": "5 years off.", 
                "notif": "Yes",
                "link": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive#:~:text=First%20unprovoked%20epileptic%20seizure"
            }
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI (STEMI/NSTEMI)": {
                "g1": "1 week (if PCI/LVEF>40%) else 4 weeks.", 
                "g2": "6 weeks off.", 
                "notif": "No (G1)",
                "link": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive#:~:text=Acute%20coronary%20syndrome"
            },
            "Pacemaker Implantation": {
                "g1": "1 week off.", 
                "g2": "6 weeks off.", 
                "notif": "Yes",
                "link": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive#:~:text=Pacemaker%20insertion"
            }
        }
    },
    # Note: I have truncated the list here for code brevity, but you can add more links using the same format!
}

# --- HEADER ---
st.title("🩺 DVLA Clinical Navigator (Deep-Link Edition)")

# --- NAVIGATION ---
col_chap, col_cond = st.columns(2)

with col_chap:
    selected_chapter = st.selectbox("📁 Select Chapter", options=list(DVLA_GUIDELINES.keys()), key="chap_select")

with col_cond:
    condition_list = list(DVLA_GUIDELINES[selected_chapter]["conditions"].keys())
    selected_condition = st.selectbox("🔬 Select Condition", options=condition_list, key="cond_select")

# --- RESULTS & DEEP LINK BUTTON ---
res = DVLA_GUIDELINES[selected_chapter]["conditions"][selected_condition]
st.divider()

col_info, col_link = st.columns([3, 1])
with col_info:
    st.subheader(f"Guidance: {selected_condition}")
with col_link:
    # This button now opens the specific highlight
    st.link_button("🔗 Open & Highlight on GOV.UK", res["link"])

# --- SIDEBAR: CALCULATOR ---
with st.sidebar:
    st.header("⏳ Cessation Calculation")
    event_date = st.date_input("Date of Event:", value=date.today())
    calc_unit = st.radio("Calculate in:", ["Weeks", "Months"], horizontal=True)
    
    if calc_unit == "Weeks":
        duration = st.number_input("Number of Weeks:", min_value=0, max_value=52, value=4)
        resume_date = event_date + timedelta(weeks=duration)
    else:
        duration = st.number_input("Number of Months:", min_value=0, max_value=60, value=1)
        resume_date = event_date + timedelta(days=int(duration * 30.44))
    
    st.metric("Earliest Resume Date", resume_date.strftime('%d/%m/%Y'))

# --- NOTIFICATION & GROUP ADVICE ---
notif_color = "#D32F2F" if "yes" in res['notif'].lower() else "#388E3C"
st.markdown(f"#### Notification Status: <span style='color:{notif_color}'>{res['notif']}</span>", unsafe_allow_html=True)

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
