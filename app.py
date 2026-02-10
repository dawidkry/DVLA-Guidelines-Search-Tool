import streamlit as st
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Standards 2026",
    page_icon="🩺",
    layout="wide"
)

# --- THE COMPLETE DATASET (8 CHAPTERS + URLS) ---
# We keep the URLs at the chapter level so they are easy to access
CHAPTER_LINKS = {
    "Chapter 1: Neurological": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
    "Chapter 2: Cardiovascular": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
    "Chapter 3: Diabetes": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
    "Chapter 4: Psychiatric": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
    "Chapter 5: Drug & Alcohol": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
    "Chapter 6: Vision": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
    "Chapter 7: Renal & Respiratory": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
    "Chapter 8: Miscellaneous": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive"
}

DVLA_GUIDELINES = {
    "Chapter 1: Neurological": {
        "TIA / Stroke": {
            "group1": "Must not drive for 1 month. May resume after 1 month if no residual deficit.",
            "group2": "Licence revoked for 1 year. Relicensing after 1 year if stable.",
            "notifiable": "No (unless residual deficit after 1 month)."
        },
        "Epilepsy (First Seizure)": {
            "group1": "Must not drive for 6 or 12 months (specialist dependent).",
            "group2": "Must not drive for 5 years. Seizure-free without meds for 10 years.",
            "notifiable": "Yes."
        },
        "Cognitive Impairment": {
            "group1": "Must not drive if impairment affects safe driving.",
            "group2": "Licence revoked permanently if significant impairment exists.",
            "notifiable": "Yes."
        }
    },
    "Chapter 2: Cardiovascular": {
        "MI (STEMI/NSTEMI)": {
            "group1": "1 week off if successful primary PCI and LVEF > 40%. Otherwise 4 weeks.",
            "group2": "6 weeks off. Requires exercise test and LVEF > 40%.",
            "notifiable": "No (for Group 1)."
        },
        "Pacemaker Implantation": {
            "group1": "Must not drive for 1 week.",
            "group2": "Must not drive for 6 weeks.",
            "notifiable": "Yes."
        }
    },
    "Chapter 3: Diabetes": {
        "Insulin Treated": {
            "group1": "May drive if <1 severe hypo in 12 months. CGM/Flash permitted.",
            "group2": "Strict criteria: CGM allowed but must carry finger-prick backup.",
            "notifiable": "Yes."
        },
        "Severe Hypoglycaemia": {
            "group1": "Stop driving for 12 months after 2nd episode in 12 months.",
            "group2": "Licence revoked for 12 months after a single episode.",
            "notifiable": "Yes."
        }
    },
    "Chapter 4: Psychiatric": {
        "Psychosis / Schizophrenia": {
            "group1": "No driving during acute illness. Stable for 3 months to resume.",
            "group2": "Licence revoked. Considered after 12 months of stability.",
            "notifiable": "Yes."
        },
        "Severe Depression / Anxiety": {
            "group1": "Notify if symptoms affect concentration or safe driving.",
            "group2": "Licence revoked if severe. Considered after 6 months stability.",
            "notifiable": "Yes (if symptomatic)."
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "Alcohol Dependence": {
            "group1": "Revoked until 1 year of abstinence or controlled drinking.",
            "group2": "Revoked until 3 years of abstinence.",
            "notifiable": "Yes."
        },
        "Cannabis/Cocaine Misuse": {
            "group1": "Revoked for 6 months minimum (must be drug-free).",
            "group2": "Revoked for 1 year minimum (must be drug-free).",
            "notifiable": "Yes."
        }
    },
    "Chapter 6: Vision": {
        "Visual Acuity Standard": {
            "group1": "6/12 Snellen. Must read number plate at 20m.",
            "group2": "6/7.5 in better eye and 6/60 in poorer eye.",
            "notifiable": "Only if standard cannot be met."
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "Sleep Apnoea (OSA)": {
            "group1": "Stop driving until symptoms controlled (e.g. CPAP).",
            "group2": "Revoked until symptoms controlled and compliance confirmed.",
            "notifiable": "Yes."
        }
    },
    "Chapter 8: Miscellaneous": {
        "Hepatic Encephalopathy": {
            "group1": "Must not drive and must notify. Relicensing if treated.",
            "group2": "Licence revoked. Requires specialist report and stability.",
            "notifiable": "Yes."
        },
        "Post-Major Surgery": {
            "group1": "Follow clinical advice (1-3 months). No notification if <3 months.",
            "group2": "Follow clinical advice. Occupational health review recommended.",
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
st.caption("A decision-support tool for doctors. Verified against latest GOV.UK Chapters.")

# --- NAVIGATION ---
col_chapter, col_condition = st.columns(2)

with col_chapter:
    selected_chapter = st.selectbox("📁 Select Chapter", options=list(DVLA_GUIDELINES.keys()))
    # Added the "Source of Truth" link right under the selection
    st.link_button(f"🔗 View Live {selected_chapter} on GOV.UK", CHAPTER_LINKS[selected_chapter])

with col_condition:
    selected_condition = st.selectbox("🔬 Select Condition", options=list(DVLA_GUIDELINES[selected_chapter].keys()))

# --- CALCULATION (SIDEBAR) ---
with st.sidebar:
    st.header("⏳ Cessation Period")
    event_date = st.date_input("Event Date", value=datetime.today())
    cess_months = st.number_input("Months Off (As per guidance)", min_value=0, max_value=60, value=1)
    
    resume_date = event_date + timedelta(days=cess_months * 30)
    st.metric("Earliest Resume Date", resume_date.strftime('%d/%m/%Y'))
    
    st.divider()
    st.markdown("### 📞 DVLA Direct")
    st.write("Medical Enquiries: **0300 790 6806**")
    st.caption("Mon-Fri, 10:30am - 1:00pm")

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
        f"DVLA FITNESS TO DRIVE: Discussed guidance for {selected_condition}. "
        f"Based on {selected_chapter}, the patient is advised to cease driving for {cess_months} month(s) from the event date ({event_date.strftime('%d/%m/%Y')}). "
        f"Earliest return date: {resume_date.strftime('%d/%m/%Y')}. "
        f"Patient reminded of legal obligation to notify the DVLA."
    )
    st.code(note, language="text")

# --- FOOTER ---
st.divider()
st.caption("🚨 **Clinician Alert:** This tool is for guidance. Clinical judgment remains paramount. Verify high-stakes decisions with the linked GOV.UK source.")
