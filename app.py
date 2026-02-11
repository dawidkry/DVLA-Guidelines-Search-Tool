import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards", page_icon="🩺", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display:none !important;}
    
    .dash-box { background-color: #000000; color: #ffffff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .ref-box { background-color: #f1f3f5; color: #1a1a1a; padding: 20px; border-left: 8px solid #005eb8; border-radius: 4px; font-size: 1.1em; }
    .appendix-header { color: #005eb8; font-weight: bold; margin-top: 20px; border-bottom: 2px solid #005eb8; padding-bottom: 5px; }
    .disclaimer-banner { background-color: #440000; color: #FFCCCC; padding: 15px; border-radius: 5px; border: 2px solid #FF0000; text-align: center; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- THE FULL RESTORED CLINICAL DATABASE ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke (Single)": {"g1": "1 month off.", "g2": "1 year off.", "notif": "No (if no deficit)", "ref": "Must not drive for 1 month. Resume if no residual deficit (motor, visual, or cognitive)."},
            "TIA / Stroke (Recurrent)": {"g1": "3 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Multiple events in short succession require 3 months cessation for Group 1."},
            "Epilepsy (Unprovoked)": {"g1": "12 months off.", "g2": "10 years off.", "notif": "Yes", "ref": "12 months standard. 6 months if low risk (<2% per annum). G2: 10 years free of meds."},
            "Seizure (Provoked - Acute Factor)": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Includes alcohol withdrawal or acute head injury seizure within 24h."},
            "Seizure (Sleep-only Pattern)": {"g1": "1-3 years stability.", "g2": "Revoked.", "notif": "Yes", "ref": "1 year if established sleep pattern; 3 years if pattern not yet stable."},
            "Subarachnoid Haemorrhage": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if successfully treated (coiled/clipped) and no deficit."},
            "Meningioma (Benign)": {"g1": "6 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "6 months if surgery performed and no seizures or deficit."},
            "Glioblastoma (Grade IV)": {"g1": "2 years off.", "g2": "Revoked.", "notif": "Yes", "ref": "2 years cessation from completion of primary treatment."},
            "Parkinson's Disease": {"g1": "Notify DVLA.", "g2": "Revoked.", "notif": "Yes", "ref": "Focus on motor control, 'off' periods, and cognitive stability."},
            "Narcolepsy / Cataplexy": {"g1": "Stop until controlled.", "g2": "Revoked.", "notif": "Yes", "ref": "Must cease until symptoms controlled and specialist confirms safety."},
            "Dementia / Cognitive Impairment": {"g1": "Notify/Review.", "g2": "Revoked.", "notif": "Yes", "ref": "Licensing depends on MoCA/MMSE scores and on-road assessment."},
            "Multiple Sclerosis": {"g1": "Notify DVLA.", "g2": "Revoked.", "notif": "Yes", "ref": "Usually 1-3 year medical review licenses granted if no disabling symptoms."},
        }
    },
    "Chapter 2: Cardiovascular & Syncope/TLoC": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Simple Vasovagal Syncope": {"g1": "No restriction.", "g2": "No restriction.", "notif": "No", "ref": "Must have clear prodrome while standing/sitting. Not allowed if occurred while driving."},
            "Unexplained TLoC (Low Risk)": {"g1": "6 months off.", "g2": "12 months off.", "notif": "Yes", "ref": "Single episode, normal ECG, no structural heart disease."},
            "Unexplained TLoC (High Risk)": {"g1": "12 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "Abnormal ECG, exertional, or occurred while sitting/lying."},
            "Cough Syncope": {"g1": "6 months off.", "g2": "5 years off.", "notif": "Yes", "ref": "6 months from the last event for G1; 5 years for G2."},
            "Syncope (CV Cause Identified)": {"g1": "4 weeks off.", "g2": "3 months off.", "notif": "Yes", "ref": "Resume once underlying cause effectively treated (e.g. pacemaker)."},
            "Syncope (Postural Hypotension)": {"g1": "Stop until treated.", "g2": "3 months off.", "notif": "Yes", "ref": "May resume when symptoms resolved and BP controlled."},
            "ACS (PCI performed)": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "No (G1)", "ref": "1 week if: Successful PCI, LVEF >40%, no other planned procedures."},
            "ICD (Symptomatic/Shock)": {"g1": "6 months off.", "g2": "Permanent Bar.", "notif": "Yes", "ref": "6 months from last shock. G2 is permanently disqualified."},
            "Pacemaker Insertion": {"g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes", "ref": "1 week (G1) or 6 weeks (G2) following surgery."},
            "Aneurysm (Thoracic >6.5cm)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "G1 notify if >6.0cm. Disqualified if >6.5cm. G2 disqualified >5.5cm."},
            "Brugada Syndrome": {"g1": "No restriction.", "g2": "Notify/Review.", "notif": "G2 Yes", "ref": "G2 requires specialist report confirming low risk."},
            "Heart Failure (NYHA IV)": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must not drive if symptoms occur at rest or minimal exertion."},
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Monitor glucose <2h before driving and every 2h while driving."},
            "Severe Hypoglycaemia (x2 in 12m)": {"g1": "12 months off.", "g2": "Revoked.", "notif": "Yes", "ref": "G1 revoked if 2 episodes requiring help occur in 1 year."},
            "Hypo Unawareness": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Must regain awareness before license reinstatement."},
            "Metformin Only": {"g1": "No notification.", "g2": "No notification.", "notif": "No", "ref": "No notification unless severe hypos or visual complications occur."},
            "Sulfonylurea (Gliclazide)": {"g1": "No (usually).", "g2": "Notify DVLA.", "notif": "G2 Yes", "ref": "G2 must notify for all insulin secretagogues."},
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Must be compliant and free from side effects."},
            "Mania / Bipolar": {"g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes", "ref": "Stability period starts from resolution of acute episode."},
            "Severe Depression": {"g1": "Clinical Pass.", "g2": "6 months stable.", "notif": "If severe", "ref": "Notify if symptoms affect concentration or involve suicidal ideation."},
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {"g1": "1 year off.", "g2": "3 years off.", "notif": "Yes", "ref": "1 year (G1) or 3 years (G2) abstinence or controlled drinking."},
            "Cannabis / Cocaine Misuse": {"g1": "6-12 months off.", "g2": "1 year off.", "notif": "Yes", "ref": "Clinical freedom from misuse for specified period."},
        }
    },
    "Chapter 6: Visual": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Acuity Standard": {"g1": "6/12 + 20m plate.", "g2": "6/7.5 + 6/60.", "notif": "No", "ref": "Must read 79mm plate at 20m. Horizontal field 120 deg required."},
            "Glaucoma (Advanced)": {"g1": "Notify DVLA.", "g2": "Notify DVLA.", "notif": "Yes", "ref": "Licensing depends on binocular Esterman field test results."},
            "Diplopia": {"g1": "Stop driving.", "g2": "Stop driving.", "notif": "Yes", "ref": "Resume if controlled by patch or prisms."},
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {"g1": "Stop until CPAP.", "g2": "Stop until CPAP.", "notif": "Yes", "ref": "Notify DVLA. Resume when CPAP control confirmed."},
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Age 70+": {"g1": "3yr renewal.", "g2": "N/A.", "notif": "Yes", "ref": "Must renew Group 1 license every 3 years from age 70."},
            "Abdominal Surgery": {"g1": "4-6 weeks off.", "g2": "Review.", "notif": "No", "ref": "Resume when emergency stop possible and pain-free."},
        }
    }
}

# --- DASHBOARD HEADER ---
st.markdown('<div class="dash-box"><h1>🩺 DVLA Clinical Standards Dashboard 2026</h1></div>', unsafe_allow_html=True)

# CALCULATOR ROW
col_c1, col_c2, col_c3, col_c4 = st.columns([1.5, 1, 1, 1.5])
with col_c1: evt_date = st.date_input("🗓️ Date of Event:", value=date.today())
with col_c2: unit = st.radio("Unit:", ["Weeks", "Months"], horizontal=True)
with col_c3: num = st.number_input(f"No. {unit}:", min_value=0, value=1)
with col_c4:
    delta = timedelta(weeks=num) if unit == "Weeks" else timedelta(days=int(num * 30.44))
    res_date = evt_date + delta
    st.metric("Potential Resume Date", res_date.strftime('%d/%m/%Y'))

st.divider()

# SELECTOR & SOURCE LINK
c1, c2 = st.columns(2)
with c1: chap = st.selectbox("📁 System Chapter", options=list(DVLA_DATA.keys()))
with c2: cond = st.selectbox("🔬 Clinical Condition", options=list(DVLA_DATA[chap]["conditions"].keys()))

st.link_button(f"🔗 Open Official GOV.UK {chap}", DVLA_DATA[chap]["url"])

res = DVLA_DATA[chap]["conditions"][cond]

# RESULTS
v1, v2, v3 = st.columns([1, 1.5, 1.5])
with v1:
    notif_color = "#d32f2f" if "yes" in res['notif'].lower() else "#2e7d32"
    st.markdown(f"**🔔 Notifiable?**\n\n<span style='color:{notif_color}; font-size: 1.8em; font-weight: bold;'>{res['notif']}</span>", unsafe_allow_html=True)
with v2: st.info(f"**🚗 Group 1**\n\n{res['g1']}")
with v3: st.warning(f"**🚛 Group 2**\n\n{res['g2']}")

st.divider()
st.subheader("📖 Official Regulatory Reference")
st.markdown(f'<div class="ref-box">{res["ref"]}</div>', unsafe_allow_html=True)

st.divider()
st.subheader("🖋️ Proposed Medical Entry")
st.code(f"DVLA FITNESS TO DRIVE ASSESSMENT:\nClinical Context: {cond}\nRegulatory Guidance: {res['ref']}\nAdvice: Cease driving for {num} {unit.lower()} from {evt_date.strftime('%d/%m/%Y')}.\nEarliest Potential Resume: {res_date.strftime('%d/%m/%Y')}\nDVLA Notification Required: {res['notif']}.", language="text")

# --- COLLAPSIBLE APPENDIX D SECTION ---
st.markdown('<h2 class="appendix-header">Appendix D</h2>', unsafe_allow_html=True)

with st.expander("📖 1. Overview: TLoC and Altered Awareness"):
    st.markdown("""
    **Driving standards for non-traumatic transient loss of consciousness.**
    Transient loss of consciousness (TLoC) or ‘blackout’ unrelated to trauma is very common and affects up to half the population in the UK at some point in their lives.

    TLoC is a state of real or apparent loss if consciousness which is associated with loss of awareness, amnesia for the period of unconsciousness, abnormal motor control, and loss of responsiveness. The condition is of short duration.

    Following an episode of transient loss of consciousness, Group 1 and Group 2 drivers should be assessed as soon as possible by a healthcare professional to advise regarding driving implications as set out in this guidance.

    If a healthcare professional can attribute a diagnosis to the episode(s) of TLoC then the relevant medical standard for that diagnosis will be applied from the appropriate section of this guide (neurological disorders, cardiovascular disorders or diabetes mellitus).

    If a diagnosis cannot be attributed, or until a diagnosis is established, the standard for “unexplained loss of consciousness” will apply.

    **Causes of transient loss of consciousness relevant to driving include:**
    * **syncope** - see relevant section of this guidance
    * **epilepsy and seizures** - see relevant section of the Neurological disorders guidance
    * **hypoglycaemia** - see relevant section of the Diabetes mellitus guidance
    * **unexplained** - see relevant section of this guidance

    Other diagnosed causes of loss of consciousness will only require notification to DVLA and subsequent enquiry if medical opinion considers that they are relevant to driving. This will include episodes clinically attributed to Postural Orthostatic Tachycardia Syndrome (POTS) and orthostatic hypotension.
    """)

with st.expander("🫀 2. Syncope and Reflex Syncope Definitions"):
    st.markdown("""
    ### Syncope
    Syncope is defined as transient loss of consciousness due to cerebral hypoperfusion, characterised by a rapid onset, short duration, and spontaneous complete recovery.

    The term presyncope describes symptoms and signs of cerebral hypoperfusion that occur before complete loss of consciousness. For licensing decisions, an episode of presyncope without progression to TLoC is relevant if medical opinion considers that the presyncope has caused an individual to be unable to safely control or stop a vehicle. In such cases, the standards for syncope will apply.

    **Causes of syncope relevant to driving include:**
    * reflex syncope (vasovagal/neurocardiogenic syncope and situational syncope)
    * cardiac causes of syncope including arrhythmia and structural heart disease (including valve disease, pulmonary arterial hypertension, cardiomyopathy, and Brugada Syndrome)

    ### Reflex syncope
    The application of medical standards for reflex syncope requires a positive diagnosis based on clinical assessment and investigations. The diagnosis of reflex syncope is made on the balance of probability and if a clinician cannot attribute a cause of syncope, the standard for unexplained transient loss of consciousness will apply.

    Reflex syncope can be associated with either or both:
    * **prodrome**, such as sweating or feeling warm/hot before loss of consciousness
    * **provocation**, such as pain, emotional stress or a medical procedure

    Some episodes of reflex syncope are related to micturition, defecation, or swallowing (‘situational’ syncope).

    A **‘reliable prodrome’** occurs predictably before syncope, is recognised by the driver as a warning of impending loss of consciousness and should be of sufficient duration to allow the driver to safely stop the vehicle.

    An **‘avoidable provocation’** includes factors that may provoke syncope, but which can be avoided and are not expected to occur while driving, such as exposure to a medical procedure, or syncope after a prolonged period of standing (for example, soldier on parade).
    """)

with st.expander("🚗 3. Reflex Syncope Standards (With & Without Prodrome)"):
    st.markdown("""
    #### Reflex syncope (vasovagal) with a reliable prodrome
    | Condition | Group 1 (Car/Motorcycle) | Group 2 (Bus/Lorry) |
    | :--- | :--- | :--- |
    | **Single episode** | **✓** If syncope has not occurred while driving, may drive and need not notify DVLA.<br>**✘** If syncope has occurred while driving, then must not drive and need not notify DVLA. Driving may resume one month following the episode of syncope. | **!** Must notify DVLA. Should a further episode occur within 24 months the guidance for multiple episodes will apply.<br>**✓** If syncope was associated with an avoidable provocation and did not occur while driving, may resume driving after recovery.<br>**✘** If syncope was not associated with an avoidable provocation, or syncope occurred while driving, must not drive. Driving may resume 3 months following subject to report.*** |
    | **Multiple episodes** (2+ in 24m) | **✓** If syncope has not occurred while driving, may drive and need not notify DVLA.<br>**✘** If syncope has occurred while driving, must not drive and must notify DVLA. Driving may resume 3 months following most recent episode. | **✘** Must notify DVLA and must not drive.<br>**✓** If syncope is associated with an avoidable provocation and has not occurred while driving, may resume driving after recovery.<br>**✘** If syncope is not associated with an avoidable provocation or has occurred while driving, must not drive. Driving may resume 6 months following subject to report.*** |

    #### Reflex syncope without a reliable prodrome
    | Condition | Group 1 (Car/Motorcycle) | Group 2 (Bus/Lorry) |
    | :--- | : :--- | :--- |
    | **Single episode** | **✘** Must not drive and must notify DVLA.<br>**✓** If syncope was associated with avoidable provocation and did not occur while driving, resume after recovery.<br>**✘** If not associated with avoidable provocation or occurred while driving, resume after 3 months. | **✘** Must not drive and must notify DVLA.<br>**!** If associated with avoidable provocation and did not occur while driving, resume after 3 months subject to report.***<br>**!** If not associated with avoidable provocation or occurred while driving, resume after 12 months subject to report.*** |
    | **Multiple episodes*** | **✘** Must not drive and must notify DVLA.<br>**✓** If associated with avoidable provocation and not while driving, resume after 3 months.<br>**✘** If not associated with avoidable provocation or occurred while driving, resume after 6 months. | **✘** Must not drive and must notify DVLA.<br>**!** Relicensing may be considered 12 months following subject to report.*** |
    """)



with st.expander("❓ 4. Unexplained Loss of Consciousness"):
    st.markdown("""
    #### Unexplained loss of consciousness (without seizure markers)
    | Condition | Group 1 (Car/Motorcycle) | Group 2 (Bus/Lorry) |
    | :--- | :--- | :--- |
    | **Single episode** | **✘** Must notify DVLA. Resume 6 months after the episode. | **✘** Must notify DVLA. Licence revoked for 12 months. |
    | **Multiple episodes**** | **✘** Must notify DVLA. Licence revoked for 12 months after most recent episode. | **✘** Must notify DVLA. Licence revoked for 5 years after most recent episode. |
    
    **Note:**
    ***An **“appropriate specialist”** includes clinicians who undertake independent decision making in neurology, cardiology, or syncope clinics.
    The report must include confidence in diagnosis, driving history, prodrome/provocation details, and risk opinion against the 20%/2% annual thresholds.
    """)

with st.expander("🧠 5. Blackouts with Seizure Markers"):
    st.markdown("""
    Clinical suspicion of a seizure but no definite evidence. Requires specialist assessment and investigation (EEG/Brain Scan).
    **Likely seizure factors:** LOC > 5m, Amnesia > 5m, Injury, Tongue biting, Incontinence, Post-ictal confusion, Headache.

    | Condition | Group 1 (Car/Motorcycle) | Group 2 (Bus/Lorry) |
    | :--- | :--- | :--- |
    | **Isolated episode** | **✘** Stop driving/Notify. 6 months off. (12 months if high risk). | **✘** Stop driving/Notify. 5 years off. |
    | **Recurrent episodes** | **✘** Standards for isolated seizure or epilepsy apply. | **✘** Standards for isolated seizure or epilepsy apply. |
    """)

with st.expander("💨 6. Cough Syncope Standards"):
    st.markdown("""
    Cough syncope identification places the person in a higher risk group. Treatment of the underlying cause **does not** reduce the risk of further episodes.

    | Condition | Group 1 (Car/Motorcycle) | Group 2 (Bus/Lorry) |
    | :--- | :--- | :--- |
    | **Cough Syncope** | **✘** Must notify. 6 months off for single; 12 months off for multiple (over 5 years). | **✘** Must notify. 12 months off for single; 5 years off for multiple (over 5 years). |
    *If more than one episode occurs within 24 hours, it counts as a single event. Episodes >24 hours apart are multiple.*
    """)

st.markdown('<div class="disclaimer-banner"><strong>⚠️ DISCLAIMER:</strong> Decision-support only. Always verify at GOV.UK.</div>', unsafe_allow_html=True)
