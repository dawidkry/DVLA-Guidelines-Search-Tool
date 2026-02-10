import streamlit as st
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Guidance Tool",
    page_icon="🩺",
    layout="wide"
)

# --- THE DATA (Organized by DVLA Chapters) ---
# Updated with 2026 guidance (e.g., CGM for Group 2)
DVLA_GUIDELINES = {
    "Chapter 1: Neurological": {
        "TIA / Stroke": {
            "group1": "Must not drive for 1 month. May resume after 1 month if no residual deficit.",
            "group2": "Licence revoked for 1 year. Can be relicensed after 1 year if stable and imaging is clear.",
            "notifiable": "No (unless residual deficit after 1 month)."
        },
        "Epilepsy (First Seizure)": {
            "group1": "Must not drive for 6 or 12 months (specialist dependent).",
            "group2": "Must not drive for 5 years. Must be seizure-free without meds for 10 years.",
            "notifiable": "Yes."
        },
        "Parkinson's Disease": {
            "group1": "May drive as long as safe vehicle control is maintained. Must notify DVLA.",
            "group2": "Licence usually revoked unless very mild and stable.",
            "notifiable": "Yes."
        }
    },
    "Chapter 2: Cardiovascular": {
        "Myocardial Infarction (STEMI/NSTEMI)": {
            "group1": "Must not drive for 1 week if successful primary PCI and LVEF > 40%. Otherwise 4 weeks.",
            "group2": "Must not drive for 6 weeks. Requires exercise test and LVEF > 40% to resume.",
            "notifiable": "No (for Group 1)."
        },
        "Aortic Aneurysm (Abdominal)": {
            "group1": "No restriction if < 6cm. Notify if 6cm - 6.4cm. Disqualified if > 6.5cm.",
            "group2": "Disqualified if > 5.5cm.",
            "notifiable": "Depends on size (Notify if > 6cm)."
        }
    },
    "Chapter 3: Diabetes": {
        "Insulin Treated (on CGM)": {
            "group1": "Must notify DVLA. Must monitor glucose (CGM/Flash allowed 2026).",
            "group2": "Strict criteria: CGM now permitted for monitoring but finger-prick backup required.",
            "notifiable": "Yes."
        },
        "Hypoglycaemia (Severe)": {
            "group1": "Must not drive if >1 episode of severe hypo in 12 months.",
            "group2": "Licence revoked. Must show 12 months of 'full awareness' and zero severe hypos.",
            "notifiable": "Yes."
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "Obstructive Sleep Apnoea (OSA)": {
            "group1": "Must not drive if causing excessive daytime sleepiness. May resume when controlled (e.g. CPAP).",
            "group2": "Licence revoked until symptoms controlled and specialist review confirms compliance.",
            "notifiable": "Yes (if symptomatic)."
        }
    }
}

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stSelectbox label { font-weight: bold; color: #004b87; }
    .reportview-container .main .block-container{ padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CLINICAL TOOLS ---
with st.sidebar:
    st.header("📅 Timeline Calculator")
    event_date = st.date_input("Date of Event/Diagnosis:", value=datetime.now())
    duration = st.selectbox("Recommended Cessation:", 
                            options=[1, 2, 3, 6, 12, 60], 
                            format_func=lambda x: f"{x} Months")
    
    # Calculate date
    resume_date = event_date + timedelta(days=(duration * 30))
    st.success(f"**Earliest Resume Date:**\n\n{resume_date.strftime('%d %B %Y')}")
    
    st.divider()
    st.markdown("### 📞 Specialist Support")
    st.info("**DVLA Medical Adviser (Doc-to-Doc):**\n\n01792 782337\n(10:30 - 13:00)")

# --- MAIN UI ---
st.title("🩺 DVLA Medical Standards Navigator")
st.write("Select the relevant chapter and condition to view the current fitness-to-drive requirements.")

# Selection Logic
col_a, col_b = st.columns(2)

with col_a:
    chapter = st.selectbox("1. Select Category / System:", options=list(DVLA_GUIDELINES.keys()))

with col_b:
    condition_list = list(DVLA_GUIDELINES[chapter].keys())
    condition = st.selectbox("2. Select Condition:", options=condition_list)

# Display Findings
if chapter and condition:
    data = DVLA_GUIDELINES[chapter][condition]
    
    st.divider()
    
    # Notification Header
    notif_text = data['notifiable']
    color = "#d32f2f" if "yes" in notif_text.lower() else "#2e7d32"
    st.markdown(f"### Notification Required? <span style='color:{color}'>{notif_text}</span>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚗 Group 1")
        st.caption("Cars and Motorcycles")
        st.info(data['group1'])
        
    with col2:
        st.subheader("🚛 Group 2")
        st.caption("Bus and Lorry")
        st.warning(data['group2'])

    # Discharge Summary Template
    st.divider()
    st.subheader("📝 Discharge Summary / Clinic Note")
    
    summary_text = (
        f"The patient was advised regarding DVLA fitness to drive standards for {condition}. "
        f"Based on Chapter {chapter.split(':')[0]} of the DVLA medical standards, "
        f"they must cease driving for a minimum of {duration} months. "
        f"Earliest date to resume (subject to recovery): {resume_date.strftime('%d/%m/%Y')}. "
        f"The patient has been reminded of their legal obligation to notify the DVLA."
    )
    
    st.text_area("Copy and paste to record:", value=summary_text, height=120)

# --- FOOTER ---
st.divider()
st.caption("⚠️ **Note for Clinicians:** This tool uses a subset of data for demonstration. Always verify with the full 'Assessing fitness to drive' guide on GOV.UK before finalising advice.")
