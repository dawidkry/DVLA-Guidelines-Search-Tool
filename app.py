import streamlit as st
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Standards 2026",
    page_icon="🩺",
    layout="wide"
)

# --- THE DATASET (8 CHAPTERS + URLS) ---
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
        "Syncope (Simple Faint)": {
            "group1": "No restriction if there is an identifiable prodrome and no recurrence.",
            "group2": "No restriction unless recurring or no prodrome. Must not drive if occurred while sitting/standing.",
            "notifiable": "No."
        },
        "Syncope (Unexplained TLoC)": {
            "group1": "6 months off if low risk; 12 months if high risk. Specialist review usually required.",
            "group2": "Licence revoked for 12 months. Relicensing depends on cause.",
            "notifiable": "Yes."
        },
        "TIA / Stroke": {
            "group1": "Must not drive for 1 month. May resume if no residual deficit.",
            "group2": "Licence revoked for 1 year. Relicensing after 1 year if stable.",
            "notifiable": "No (unless residual deficit)."
        },
        "Epilepsy (First Seizure)": {
            "group1": "Must not drive for 6 or 12 months.",
            "group2": "Must not drive for 5 years.",
            "notifiable": "Yes."
        }
    },
    "Chapter 2: Cardiovascular": {
        "MI (STEMI/NSTEMI)": {
            "group1": "1 week off if successful primary PCI and LVEF > 40%. Otherwise 4 weeks.",
            "group2": "6 weeks off. Requires exercise test and LVEF > 40%.",
            "notifiable": "No (for Group 1)."
        },
        "Arrhythmia (Symptomatic)": {
            "group1": "Must stop driving if arrhythmia has caused or is likely to cause incapacity.",
            "group2": "Licence revoked until arrhythmia controlled for 3 months.",
            "notifiable": "Yes."
        }
    },
    "Chapter 3: Diabetes": {
        "Insulin Treated": {
            "group1": "May drive if <1 severe hypo in 12 months. CGM/Flash permitted.",
            "group2": "Strict criteria: CGM allowed but must carry finger-prick backup.",
            "notifiable": "Yes."
        }
    },
    "Chapter 4: Psychiatric": {
        "Psychosis / Schizophrenia": {
            "group1": "No driving during acute illness. Stable for 3 months to resume.",
            "group2": "Licence revoked. Considered after 12 months of stability.",
            "notifiable": "Yes."
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "Alcohol Dependence": {
            "group1": "Revoked until 1 year of abstinence or controlled drinking.",
            "group2": "Revoked until 3 years of abstinence.",
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

# --- GLOBAL SEARCH FEATURE ---
search_query = st.text_input("🔍 Quick Search (e.g. 'Syncope', 'Stroke', 'Acuity'):").strip().lower()

# Logic to handle Search vs. Selection
if search_query:
    results = []
    for chap, conds in DVLA_GUIDELINES.items():
        for cond_name, details in conds.items():
            if search_query in cond_name.lower():
                results.append((chap, cond_name, details))
    
    if results:
        selected_chapter, selected_condition, res = results[0] # Pick the first match
        st.success(f"Found: **{selected_condition}** in **{selected_chapter}**")
    else:
        st.error("Condition not found. Use the dropdowns below.")
        selected_chapter = list(DVLA_GUIDELINES.keys())[0]
        selected_condition = list(DVLA_GUIDELINES[selected_chapter].keys())[0]
else:
    # --- DROPDOWN NAVIGATION ---
    col_chapter, col_condition = st.columns(2)
    with col_chapter:
        selected_chapter = st.selectbox("📁 Select Chapter", options=list(DVLA_GUIDELINES.keys()))
        st.link_button(f"🔗 View Live {selected_chapter} on GOV.UK", CHAPTER_LINKS[selected_chapter])
    with col_condition:
        selected_condition = st.selectbox("🔬 Select Condition", options=list(DVLA_GUIDELINES[selected_chapter].keys()))
    res = DVLA_GUIDELINES[selected_chapter][selected_condition]

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

# --- RESULTS DISPLAY ---
st.divider()
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
st.caption("🚨 **Clinician Alert:** This tool is for guidance. Clinical judgment remains paramount.")
