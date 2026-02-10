import streamlit as st
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Standards 2026",
    page_icon="🩺",
    layout="wide"
)

# --- DATASET (8 CHAPTERS) ---
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
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {"g1": "May drive if <1 severe hypo/year.", "g2": "Strict criteria; CGM allowed with backup.", "notif": "Yes"}
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "3 months stability to resume.", "g2": "12 months stability.", "notif": "Yes"}
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year abstinence.", "g2": "3 years abstinence.", "notif": "Yes"}
        }
    },
    "Chapter 6: Vision": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Visual Acuity Standard": {"g1": "6/12 and read plate at 20m.", "g2": "6/7.5 and 6/60 in poorer eye.", "notif": "If standard not met"}
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP control.", "g2": "Stop until compliance confirmed.", "notif": "Yes"}
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Hepatic Encephalopathy": {"g1": "Must notify. Resume if treated.", "g2": "Revoked until stable.", "notif": "Yes"},
            "Post-Major Surgery": {"g1": "Usually 1-3 months. No notification.", "g2": "Occ Health review.", "notif": "No (<3m)"}
        }
    }
}

# --- HEADER ---
st.title("🩺 DVLA Clinical Navigator")

# --- NAVIGATION WITH KEYERROR PROTECTION ---
col_chap, col_cond = st.columns(2)

with col_chap:
    # Adding a key="chap" helps Streamlit track state
    selected_chapter = st.selectbox("📁 Select Chapter", options=list(DVLA_GUIDELINES.keys()), key="chap")
    st.link_button(f"🔗 View Live {selected_chapter}", DVLA_GUIDELINES[selected_chapter]["url"])

with col_cond:
    # Dynamically fetch the condition list based on the chapter
    condition_options = list(DVLA_GUIDELINES[selected_chapter]["conditions"].keys())
    selected_condition = st.selectbox("🔬 Select Condition", options=condition_options, key="cond")

# --- SIDEBAR: DYNAMIC CALCULATOR ---
with st.sidebar:
    st.header("⏳ Cessation period")
    event_date = st.date_input("Date of Event/Diagnosis:", value=datetime.
