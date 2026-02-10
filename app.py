import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards 2026", page_icon="🩺", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display:none !important;}
    
    .dash-box {
        background-color: #000000;
        color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .ref-box {
        background-color: #f1f3f5; color: #1a1a1a; padding: 20px;
        border-left: 8px solid #005eb8; border-radius: 4px; font-size: 1.1em;
    }
    .disclaimer-banner {
        background-color: #440000; color: #FFCCCC; padding: 15px;
        border-radius: 5px; border: 2px solid #FF0000; text-align: center; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- THE MASSIVELY EXPANDED CLINICAL DATABASE ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke (Single Event)": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. Resume after 1 month if no residual deficit (visual field, cognitive, or motor)."},
            "TIA / Stroke (Multiple/Recurrent)": {"g1": "3 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Recurrent events within a short period require a 3-month cessation for Group 1."},
            "Epilepsy (Unprovoked Seizure)": {"g1": "12 months off.", "g2": "10 years off.", "notif": "Yes", "ref": "12 months standard. Can be reduced to 6 months if specialist review confirms low risk (<2%)."},
            "Seizure (Isolated Provoked - e.g. ETOH)": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Provoked by a transient factor (e.g., alcohol withdrawal). 6 months if the factor is removed."},
            "Seizure (Sleep-only Pattern)": {"g1": "1-3 years stability.", "g2": "Revoked.", "notif": "Yes", "ref": "Must have established pattern. 1 year if seizures only ever occur while asleep."},
            "Subarachnoid Haemorrhage (Aneurysmal)": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if successfully treated (coiled/clipped) and no residual neuro-deficit."},
            "Meningioma (Benign Grade I)": {"g1": "6-12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if surgery performed and no seizures. 12 months if treated with radiotherapy."},
            "Glioblastoma (Malignant Grade IV)": {"g1": "2 years off.", "g2": "Revoked.", "notif": "Yes", "ref": "Must not drive for 2 years following the completion of primary treatment (surgery/chemo/rads)."},
            "Pituitary Tumour (Craniotomy)": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "Depends on surgical approach; trans-sphenoidal may allow earlier return if fields are clear."},
            "Parkinson's Disease": {"g1": "Notify DVLA.", "g2": "Revoked.", "notif": "Yes", "ref": "Focus on motor fluctuations and 'off' periods. Group 2 is usually a bar."},
            "Multiple Sclerosis": {"g1": "Notify DVLA.", "g2": "Revoked.", "notif": "Yes", "ref": "License usually granted on a 1-3 year medical review basis if no disabling symptoms."},
            "Narcolepsy / Cataplexy": {"g1": "Stop until controlled.", "g2": "Revoked.", "notif": "Yes", "ref": "Must cease driving until symptoms controlled and specialist confirms wakefulness standards met."},
            "Dementia (MoCA >20)": {"g1": "Notify/Review.", "g2": "Revoked.", "notif": "Yes", "ref": "Group 1 may drive if on-road assessment is passed and clinical review is favourable."},
        }
    },
    "Chapter 2: Cardiovascular & TLoC": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Simple Vasovagal Syncope": {"g1": "No restriction.", "g2": "No restriction.", "notif": "No", "ref": "Clear prodrome, occurring while standing/sitting. Prohibited if event occurred while driving."},
            "Unexplained TLoC (Single - Low Risk)": {"g1": "6 months off.", "g2": "12 months off.", "notif": "Yes", "ref": "Low risk: Single episode, normal ECG, no structural heart disease."},
            "Unexplained TLoC (Single - High Risk)": {"g1": "12 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "High risk: Occurred while sitting/lying, abnormal ECG, or exertional."},
            "Cough Syncope": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months cessation from the last episode. High recurrence risk for vocational drivers."},
            "Syncope (Postural Hypotension)": {"g1": "Stop until treated.", "g2": "3 months off.", "notif": "Yes", "ref": "May resume when blood pressure is controlled and symptoms resolved."},
            "Syncope (Identified CV Cause)": {"g1": "4 weeks off.", "g2": "3 months off.", "notif": "Yes", "ref": "Resume once underlying cause (e.g. pacemaker for heart block) is treated."},
            "ACS (Successful PCI)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no further urgent procedures planned."},
            "ACS (Medical Mgmt / No PCI)": {"g1": "4 weeks off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "4 weeks mandatory cessation for Group 1 if no intervention was performed."},
            "ICD (Prophylactic)": {"g1": "1 month off.", "g2": "Permanent Bar.", "notif": "Yes", "ref": "Group 2 is permanently disqualified from holding a vocational license."},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "1 week (G1) or 6 weeks (G2) following surgery or box change."},
            "Aneurysm (Thoracic >6.5cm)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "G1 must stop until surgically repaired. G2 disqualified if >5.5cm."},
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin (Standard)": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Test blood glucose <2h before driving and every 2h while driving."},
            "Severe Hypoglycaemia (x2 in 12m)": {"g1": "12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "Revoked if 2 episodes of severe hypo (requiring third-party help) in 12 months."},
            "Hypoglycaemia Unawareness": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must not drive until awareness is regained to specialist satisfaction."},
            "Sulfonylurea (Gliclazide)": {"g1": "No notification.", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "G1 only if severe hypos occur. G2 must notify for all insulin secretagogues."},
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Must be compliant with medication and free from disabling side effects."},
            "Mania / Hypomania": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Stability period starts only after the acute episode has resolved."},
            "Severe Depression": {"g1": "Clinical Pass.", "g2": "6 months stable.", "notif": "If severe", "ref": "Notify if symptoms affect concentration, agitation, or involve suicidal ideation."},
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Acuity Standard": {"g1": "6/12 + 20m plate.", "g2": "6/7.5 + 6/60.", "notif": "No", "ref": "Must read 79mm plate at 20m. Horizontal field of 120 degrees required."},
            "Hemianopia (Complete)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "G1 'exceptional case' possible after 12 months stability and on-road test."},
            "Diplopia (Uncorrected)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Resume once stable and controlled by a patch or prisms."},
        }
    }
}

# --- CALCULATOR HEADER ---
st.markdown('<div class="dash-box"><h1>🩺 DVLA Cessation Dashboard 2026</h1></div>', unsafe_allow_html=True)
col_c1, col_c2, col_c3, col_c4 = st.columns([1.5, 1, 1, 1.5])

with col_c1: evt_date = st.date_input("🗓️ Date of Clinical Event:", value=date.today())
with col_c2: unit = st.radio("Unit:", ["Weeks", "Months"], horizontal=True)
with col_c3: num = st.number_input(f"No. {unit}:", min_value=0, value=1)
with col_c4:
    delta = timedelta(weeks=num) if unit == "Weeks" else timedelta(days=int(num * 30.44))
    res_date = evt_date + delta
    st.metric("Potential Resume Date", res_date.strftime('%d/%m/%Y'))

st.divider()

# --- SELECTOR & DYNAMIC LINK ---
c1, c2 = st.columns(2)
with c1: chap = st.selectbox("📁 System Chapter", options=list(DVLA_DATA.keys()))
with c2: cond = st.selectbox("🔬 Clinical Condition", options=list(DVLA_DATA[chap]["conditions"].keys()))

# --- THE SOURCE LINK BUTTON ---
st.link_button(f"🔗 Open Official GOV.UK Reference for {chap}", DVLA_DATA[chap]["url"])

res = DVLA_DATA[chap]["conditions"][cond]

# --- CLINICAL RESULTS ---
v1, v2, v3 = st.columns([1, 1.5, 1.5])
with v1:
    notif_color = "#d32f2f" if "yes" in res['notif'].lower() else "#2e7d32"
    st.markdown(f"**🔔 Notifiable?**\n\n<span style='color:{notif_color}; font-size: 1.8em; font-weight: bold;'>{res['notif']}</span>", unsafe_allow_html=True)
with v2: st.info(f"**🚗 Group 1 (Car/Bike)**\n\n{res['g1']}")
with v3: st.warning(f"**🚛 Group 2 (HGV/Bus)**\n\n{res['g2']}")

st.divider()
st.subheader("📖 Official Regulatory Reference")
st.markdown(f'<div class="ref-box">{res["ref"]}</div>', unsafe_allow_html=True)



st.divider()
st.subheader("🖋️ Proposed Medical Entry")
st.code(f"DVLA FITNESS TO DRIVE ASSESSMENT:\nClinical Context: {cond}\nRegulatory Guidance: {res['ref']}\nAdvice: Cease driving for {num} {unit.lower()} from {evt_date.strftime('%d/%m/%Y')}.\nEarliest Potential Resume: {res_date.strftime('%d/%m/%Y')}\nDVLA Notification Required: {res['notif']}.\nPatient informed of legal responsibility to notify DVLA if required.", language="text")



st.markdown('<div class="disclaimer-banner"><strong>⚠️ DISCLAIMER:</strong> Decision-support only. Always verify against latest guidance.</div>', unsafe_allow_html=True)
