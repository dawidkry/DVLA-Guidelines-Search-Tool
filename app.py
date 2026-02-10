import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Standards 2026",
    page_icon="🩺",
    layout="wide"
)

# --- DATASET ---
DVLA_GUIDELINES = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {"g1": "1 month off. Resume if no residual deficit.", "g2": "1 year off.", "notif": "No (unless residual deficit)"},
            "Syncope (Simple Faint)": {"g1": "No restriction if prodrome present.", "g2": "No restriction unless recurring.", "notif": "No"},
            "Syncope (Unexplained TLoC)": {"g1": "6-12 months off depending on risk.", "g2": "12 months off minimum.", "notif": "Yes"},
            "Epilepsy (First Seizure)": {"g1": "6 or 12 months off.", "g2": "5 years off.", "notif": "Yes"},
            "Parkinson's Disease": {"g1": "Drive if safe control maintained.", "g2": "Usually revoked.", "notif": "Yes"}
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI (STEMI/NSTEMI)": {"g1": "1 week (if PCI/LVEF>40%) else 4 weeks.", "g2": "6 weeks off.", "notif": "No (G1)"},
            "Pacemaker Implantation": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes"},
            "ICD (Prophylactic/Symptomatic)": {"g1": "1 to 6 months off.", "g2": "Permanent bar.", "notif": "Yes"},
            "Aortic Aneurysm (>6cm)": {"g1": "Notify. Disqualified if >6.5cm.", "g2": "Disqualified if >5.5cm.", "notif": "Yes"}
        }
    },
    "Chapter 3: Diabetes": { "url": "...", "conditions": { "Insulin Treated": {"g1": "...", "g2": "...", "notif": "Yes"} } },
    "Chapter 4: Psychiatric": { "url": "...", "conditions": { "Psychosis": {"g1": "...", "g2": "...", "notif": "Yes"} } },
    "Chapter 5: Drug & Alcohol": { "url": "...", "conditions": { "Alcohol Dependence": {"g1": "...", "g2": "...", "notif": "Yes"} } },
    "Chapter 6: Vision": { "url": "...", "conditions": { "Visual Acuity": {"g1": "...", "g2": "...", "notif": "If standard not met"} } },
    "Chapter 7: Renal & Respiratory": { "url": "...", "conditions": { "Sleep Apnoea": {"g1": "...", "g2": "...", "notif": "Yes"} } },
    "Chapter 8: Miscellaneous": { "url": "...", "conditions": { "Post-Surgery": {"g1": "...", "g2": "...", "notif": "No"} } }
}

# --- NAVIGATION ---
st.title("🩺 DVLA Clinical Navigator")

col_chap, col_cond = st.columns(2)
with col_chap:
    selected_chapter = st.selectbox("📁 Select Chapter", options=list(DVLA_GUIDELINES.keys()), key="chap")
    st.link_button(f"🔗 View Live {selected_chapter}", DVLA_GUIDELINES[selected_chapter]["url"])

with col_cond:
    condition_options = list(DVLA_GUIDELINES[selected_chapter]["conditions"].keys())
    selected_condition = st.selectbox("🔬 Select Condition", options=condition_options, key="cond")

# --- SIDEBAR: FIXED CALCULATOR ---
with st.sidebar:
    st.header("⏳ Cessation period")
    
    # FIXED LINE: Added date.today() and closed all parentheses properly
    event_date = st.date_input("Date of Event/Diagnosis:", value=date.today())
    
    calc_unit = st.radio("Calculate in:", ["Weeks", "Months"], horizontal=True)
    
    if calc_unit == "Weeks":
        duration = st.number_input("Number of Weeks:", min_value=0, max_value=52, value=1)
        resume_date = event_date + timedelta(weeks=duration)
    else:
        duration = st.number_input("Number of Months:", min_value=0, max_value=60, value=1)
        # 30.44 days is the mathematical average for a month
        resume_date = event_date + timedelta(days=int(duration * 30.44))
    
    st.metric("Earliest Resume Date", resume_date.strftime('%d/%m/%Y'))

# --- RESULTS ---
if selected_condition in DVLA_GUIDELINES[selected_chapter]["conditions"]:
    res = DVLA_GUIDELINES[selected_chapter]["conditions"][selected_condition]
    st.divider()

    notif_color = "#D32F2F" if "yes" in res['notif'].lower() else "#388E3C"
    st.markdown(f"### Notification Status: <span style='color:{notif_color}'>{res['notif']}</span>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**🚗 Group 1**\n\n{res['g1']}")
    with c2:
        st.warning(f"**🚛 Group 2**\n\n{res['g2']}")

    # --- CLINICAL NOTE ---
    st.divider()
    st.subheader("🖋️ Proposed Medical Entry")
    note = (
        f"DVLA ADVICE ({selected_condition}): Advised cessation for {duration} {calc_unit.lower()} "
        f"from {event_date.strftime('%d/%m/%Y')}. Earliest resume: {resume_date.strftime('%d/%m/%Y')}. "
        f"Patient advised of duty to notify DVLA: {res['notif']}."
    )
    st.code(note, language="text")
