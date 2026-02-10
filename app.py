import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Navigator 2026", page_icon="🩺", layout="wide")

# --- THE COMPREHENSIVE DATASET ---
# Deep links use #:~:text= to scroll and highlight the rule on GOV.UK
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {"g1": "1 month off. Resume if no residual deficit.", "g2": "1 year off. Requires stable imaging.", "notif": "No (G1)", "fragment": "Must%20not%20drive%20for%20at%20least%201%20month"},
            "Syncope (Simple Vasovagal)": {"g1": "No restriction if prodrome present.", "g2": "No restriction unless while sitting/standing.", "notif": "No", "fragment": "Simple%20vasovagal%20faint"},
            "Syncope (Unexplained TLoC)": {"g1": "6m (low risk) or 12m (high risk).", "g2": "12 months off minimum.", "notif": "Yes", "fragment": "Unexplained%20syncope"},
            "Cough Syncope": {"g1": "Stop until controlled. Notify DVLA.", "g2": "Licence revoked until asymptomatic for 3m.", "notif": "Yes", "fragment": "Cough%20syncope"},
            "Epilepsy (First Seizure)": {"g1": "6 or 12 months off.", "g2": "5 years off.", "notif": "Yes", "fragment": "First%20unprovoked%20epileptic%20seizure"},
            "Dementia": {"g1": "Must stop if safety affected.", "g2": "Permanent revocation.", "notif": "Yes", "fragment": "Dementia%20and%20cognitive%20impairment"},
            "Parkinson's": {"g1": "Drive as long as safe control maintained.", "g2": "Usually revoked.", "notif": "Yes", "fragment": "Parkinson's%20disease"}
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI (STEMI/NSTEMI)": {"g1": "1 week (if PCI/LVEF>40%) else 4 weeks.", "g2": "6 weeks off.", "notif": "No (G1)", "fragment": "Acute%20coronary%20syndrome"},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "fragment": "Pacemaker%20insertion"},
            "ICD (Symptomatic)": {"g1": "6 months off.", "g2": "Permanent bar.", "notif": "Yes", "fragment": "implantable%20cardioverter%20defibrillator"},
            "Atrial Fibrillation": {"g1": "No restriction unless symptomatic.", "g2": "6 weeks off if symptomatic.", "notif": "Only if disabling", "fragment": "Arrhythmias"},
            "Aortic Aneurysm": {"g1": "Disqualified if >6.5cm.", "g2": "Disqualified if >5.5cm.", "notif": "Yes", "fragment": "Aortic%20aneurysm"}
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin (Group 1)": {"g1": "May drive if no more than 1 severe hypo/12m.", "g2": "N/A", "notif": "Yes", "fragment": "Insulin%20treated%20diabetes"},
            "Severe Hypoglycaemia": {"g1": "12m off after 2nd episode.", "g2": "12m off after 1st episode.", "notif": "Yes", "fragment": "Severe%20hypoglycaemia"}
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis": {"g1": "3m stable to resume.", "g2": "12m stable to resume.", "notif": "Yes", "fragment": "Psychotic%20disorder"},
            "Severe Depression": {"g1": "Stop if suicidal/impaired.", "g2": "6m stability required.", "notif": "Yes", "fragment": "Severe%20depression"}
        }
    },
    "Chapter 5: Drug/Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year abstinence.", "g2": "3 years abstinence.", "notif": "Yes", "fragment": "Alcohol%20dependence"}
        }
    },
    "Chapter 6: Vision": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Visual Acuity": {"g1": "6/12 Snellen required.", "g2": "6/7.5 and 6/60 required.", "notif": "If standard not met", "fragment": "Visual%20acuity"}
        }
    },
    "Chapter 7: Renal/Resp": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea": {"g1": "Stop until CPAP control.", "g2": "Stop until compliance confirmed.", "notif": "Yes", "fragment": "Sleep%20apnoea"}
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Post-Surgery": {"g1": "1-3 months typically.", "g2": "Occ Health review.", "notif": "No", "fragment": "surgery"}
        }
    }
}

# --- NAVIGATION ---
st.title("🩺 Complete DVLA Navigator 2026")

col_chap, col_cond = st.columns(2)
with col_chap:
    chap_name = st.selectbox("📁 Chapter", options=list(DVLA_DATA.keys()), key="c_sel")
with col_cond:
    cond_name = st.selectbox("🔬 Condition", options=list(DVLA_DATA[chap_name]["conditions"].keys()), key="n_sel")

# --- DATA RETRIEVAL ---
res = DVLA_DATA[chap_name]["conditions"][cond_name]
base_url = DVLA_DATA[chap_name]["url"]
deep_link = f"{base_url}#:~:text={res['fragment']}"

# --- HIGHLIGHT BUTTON ---
st.divider()
st.link_button(f"🚀 Open & Highlight: {cond_name}", deep_link, type="primary")

# --- SIDEBAR CALCULATOR ---
with st.sidebar:
    st.header("⏳ Cessation Clock")
    event_date = st.date_input("Event Date:", value=date.today())
    unit = st.radio("Unit:", ["Weeks", "Months"], horizontal=True)
    num = st.number_input(f"Number of {unit}:", min_value=0, value=1)
    
    delta = timedelta(weeks=num) if unit == "Weeks" else timedelta(days=int(num * 30.44))
    resume = event_date + delta
    st.metric("Earliest Resume Date", resume.strftime('%d/%m/%Y'))

# --- DISPLAY SPECS ---
c1, c2 = st.columns(2)
with c1:
    st.info(f"**🚗 Group 1 (Car/Bike)**\n\n{res['g1']}")
with c2:
    st.warning(f"**🚛 Group 2 (HGV/Bus)**\n\n{res['g2']}")

# --- AUTO-NOTE ---
st.divider()
st.subheader("🖋️ Medical Entry Snippet")
st.code(f"DVLA GUIDANCE: {cond_name}. Advised {num} {unit.lower()} cessation from {event_date.strftime('%d/%m/%Y')}. Notify DVLA: {res['notif']}.", language="text")
