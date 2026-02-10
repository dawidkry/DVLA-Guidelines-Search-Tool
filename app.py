import streamlit as st
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Standards 2026",
    page_icon="🩺",
    layout="wide"
)

# --- THE COMPLETE DATASET (8 CHAPTERS) ---
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
        "Cognitive Impairment (Post-Injury)": {
            "group1": "Must not drive if impairment is likely to affect safe driving.",
            "group2": "Licence refused or revoked permanently if significant impairment exists.",
            "notifiable": "Yes."
        }
    },
    "Chapter 2: Cardiovascular": {
        "Myocardial Infarction (STEMI/NSTEMI)": {
            "group1": "Must not drive for 1 week if successful primary PCI and LVEF > 40%. Otherwise 4 weeks.",
            "group2": "Must not drive for 6 weeks. Requires exercise test and LVEF > 40%.",
            "notifiable": "No (for Group 1)."
        },
        "Pacemaker Implantation": {
            "group1": "Must not drive for 1 week.",
            "group2": "Must not drive for 6 weeks.",
            "notifiable": "Yes."
        }
    },
    "Chapter 3: Diabetes": {
        "Insulin Treated (Group 1)": {
            "group1": "May drive if no more than 1 severe hypo in 12 months. CGM/Flash permitted (2026 update).",
            "group2": "Strict criteria: CGM permitted for monitoring, but finger-prick backup required. No severe hypos in 12 months.",
            "notifiable": "Yes."
        },
        "Severe Hypoglycaemia": {
            "group1": "Must not drive for 12 months after 2nd episode in a 12-month period.",
            "group2": "Licence revoked for 12 months after a single episode.",
            "notifiable": "Yes."
        }
    },
    "Chapter 4: Psychiatric": {
        "Psychosis / Schizophrenia": {
            "group1": "Must not drive during acute illness. May be relicensed after 3 months of stability.",
            "group2": "Licence revoked. May be considered after 12 months of stability.",
            "notifiable": "Yes."
        },
        "Severe Depression / Anxiety": {
            "group1": "Must notify if symptoms (e.g. concentration/suicidal ideation) affect driving.",
            "group2": "Licence revoked if severe. Considered after 6 months of stability.",
            "notifiable": "Yes (if symptomatic)."
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "Alcohol Dependence": {
            "group1": "Licence refused/revoked until 1 year of abstinence. Controlled drinking maybe considered.",
            "group2": "Licence refused/revoked until 3 years of abstinence.",
            "notifiable": "Yes."
        },
        "Persistent Cannabis/Cocaine Misuse": {
            "group1": "Licence revoked for 6 months minimum (must be drug-free).",
            "group2": "Licence revoked for 1 year minimum (must be drug-free).",
            "notifiable": "Yes."
        }
    },
    "Chapter 6: Vision": {
        "Visual Acuity (Minimum Standard)": {
            "group1": "6/12 on Snellen scale. Must read number plate at 20m.",
            "group2": "6/7.5 in better eye and 6/60 in poorer eye.",
            "notifiable": "Only if standard cannot be met."
        },
        "Visual Field Defects": {
            "group1": "Horizontal field of 120°. No significant defect within central 20°.",
            "group2": "Horizontal field of 160°. No defect within central 30°.",
            "notifiable": "Yes."
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "Sleep Apnoea (OSA) Syndrome": {
            "group1": "Must not drive until symptoms controlled (e.g. CPAP).",
            "group2": "Licence revoked until symptoms controlled and review confirms compliance.",
            "notifiable": "Yes."
        },
        "Chronic Renal Failure (Dialysis)": {
            "group1": "May drive unless causing significant symptoms (e.g. fatigue).",
            "group2": "Licence revoked if severe symptoms present.",
            "notifiable": "No (unless symptomatic)."
        }
    },
    "Chapter 8: Miscellaneous": {
        "Hepatic Encephalopathy (New 2026)": {
            "group1": "Must not drive and must notify. Licensing considered if OHE is successfully treated.",
            "group2": "Licence revoked. Relicensing requires specialist report and long-term stability.",
            "notifiable": "Yes."
        },
        "Post-Major Surgery": {
            "group1": "Must follow clinical advice (usually 1-3 months). Generally do not notify DVLA if <3 months.",
            "group2": "Must follow clinical advice. Often requires occupational health clearance.",
            "notifiable": "No (if <3 months)."
        }
    }
}

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    h1 { color: #005eb8; } /* NHS Blue */
    .stSelectbox label { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🩺 Complete DVLA Medical Standards (2026 Edition)")
st.write("Cross-specialty tool for inpatient discharge and outpatient clinic reviews.")

# --- NAVIGATION ---
col_chapter, col_condition = st.columns(2)

with col_chapter:
    selected_chapter = st.selectbox("📁 Select Chapter", options=list(DVLA_GUIDELINES.keys()))

with col_condition:
    selected_condition = st.selectbox("🔬 Select Condition", options=list(DVLA_GUIDELINES[selected_chapter].keys()))

# --- CALCULATION (SIDEBAR) ---
with st.sidebar:
    st.header("⏳ Cessation Period")
    event_date = st.date_input("Event Date", value=datetime.today())
    cess_months = st.number_input("Months Off", min_value=0, max_value=60, value=1)
    
    resume_date = event_date + timedelta(days=cess_months * 30)
    st.metric("Earliest Resume Date", resume_date.strftime('%d/%m/%Y'))
    
    st.divider()
    st.markdown("### 📞 DVLA Direct")
    st.write("Medical Enquiries: **0300 790 6806**")

# --- RESULTS DISPLAY ---
if selected_chapter and selected_condition:
    res = DVLA_GUIDELINES[selected_chapter][selected_condition]
    
    st.divider()
    
    # Notification Banner
    notif_color = "#D32F2F" if "yes" in res['notifiable'].lower() else "#388E3C"
    st.markdown(f"### Notification Status: <span style='color:{notif_color}'>{res['notifiable']}</span>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**🚗 Group 1 (Car/Motorcycle)**\n\n{res['group1']}")
    with c2:
        st.warning(f"**🚛 Group 2 (Bus/Lorry)**\n\n{res['group2']}")

    # Clinical Note Generation
    st.divider()
    st.subheader("🖋️ Proposed Medical Entry / Discharge Advice")
    note = (
        f"Discussed DVLA fitness to drive guidance ({selected_chapter}: {selected_condition}). "
        f"The patient has been advised to cease driving for {cess_months} month(s) from the date of the event. "
        f"Earliest potential return: {resume_date.strftime('%d/%m/%Y')}. "
        f"The patient understands it is their legal responsibility to notify the DVLA."
    )
    st.code(note, language="text")

# --- FOOTER ---
st.divider()
st.caption("🚨 **Clinician Alert:** This tool is for guidance. Refer to the full GOV.UK 'Assessing fitness to drive' document for complex cases or high-risk offenders.")
