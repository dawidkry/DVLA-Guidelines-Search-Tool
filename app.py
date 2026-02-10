import streamlit as st
from datetime import datetime, timedelta, date

# --- PAGE CONFIG ---
st.set_page_config(page_title="DVLA Clinical Standards 2026", page_icon="🩺", layout="wide")

# --- DATASET (8 CHAPTERS - FULLY RESTORED & FORMATTED) ---
DVLA_DATA = {
    "Chapter 1: Neurological": {
        "url": "https://www.gov.uk/guidance/neurological-disorders-assessing-fitness-to-drive",
        "conditions": {
            "TIA / Stroke": {
                "g1": "1 month off.", "g2": "1 year off.", "notif": "No (unless residual deficit)",
                "ref": "**Official Rule:**\n* **Group 1:** Must not drive for 1 month. May resume after 1 month if no residual deficit.\n* **Group 2:** Licence revoked for 1 year. Relicensing after 1 year if stable and imaging is clear."
            },
            "Syncope (Unexplained TLoC)": {
                "g1": "6-12 months off.", "g2": "12 months off.", "notif": "Yes",
                "ref": "**Official Rule:**\n* **High Risk:** 12 months off driving.\n* **Low Risk:** 6 months off driving.\n* **Note:** Must notify DVLA in all unexplained cases."
            },
            "Epilepsy (First Seizure)": {
                "g1": "6 or 12 months off.", "g2": "5 years off.", "notif": "Yes",
                "ref": "**Official Rule:**\n* **Standard:** 6 months off if no brain scan abnormality.\n* **High Risk:** 12 months off if there is a clinical risk of recurrence."
            },
            "Parkinson's Disease": {
                "g1": "Safe control dependent.", "g2": "Usually revoked.", "notif": "Yes",
                "ref": "**Official Rule:** Must notify DVLA. Licensing depends on the ability to maintain safe control of the vehicle and lack of significant cognitive impairment."
            },
            "Dementia": {
                "g1": "Cognition dependent.", "g2": "Revoked.", "notif": "Yes",
                "ref": "**Official Rule:** Must notify DVLA. Driving may continue if impairment is mild and a formal driving assessment is passed."
            }
        }
    },
    "Chapter 2: Cardiovascular": {
        "url": "https://www.gov.uk/guidance/cardiovascular-disorders-assessing-fitness-to-drive",
        "conditions": {
            "MI (ACS)": {
                "g1": "1-4 weeks off.", "g2": "6 weeks off.", "notif": "No (G1)",
                "ref": "**Official Rule:**\n* **Group 1:** 1 week if successful PCI and LVEF > 40%. Otherwise 4 weeks.\n* **Group 2:** 6 weeks off. Requires exercise test and LVEF > 40%."
            },
            "Pacemaker Insertion": {
                "g1": "1 week off.", "g2": "6 weeks off.", "notif": "Yes",
                "ref": "**Official Rule:** Must notify DVLA. Driving must cease for 1 week for Group 1 and 6 weeks for Group 2."
            },
            "Aortic Aneurysm": {
                "g1": "Size dependent.", "g2": "Size dependent.", "notif": "Yes",
                "ref": "**Official Rule:**\n* **Group 1:** Must notify if >6.0cm. Disqualified if >6.5cm.\n* **Group 2:** Disqualified if >5.5cm."
            },
            "Atrial Fibrillation": {
                "g1": "No restriction.", "g2": "Symptom dependent.", "notif": "No (unless disabling)",
                "ref": "**Official Rule:** Drive as long as no distraction or incapacity from symptoms/arrhythmia."
            }
        }
    },
    "Chapter 3: Diabetes": {
        "url": "https://www.gov.uk/guidance/diabetes-mellitus-assessing-fitness-to-drive",
        "conditions": {
            "Insulin Treated": {
                "g1": "Glucose control dependent.", "g2": "Strict criteria.", "notif": "Yes",
                "ref": "**Official Rule:** Must notify. Group 1: No more than 1 severe hypo in 12 months. Must use CGM/Finger-prick as per 2026 standards."
            }
        }
    },
    "Chapter 4: Psychiatric": {
        "url": "https://www.gov.uk/guidance/psychiatric-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Psychosis / Schizophrenia": {
                "g1": "3 months stable.", "g2": "12 months stable.", "notif": "Yes",
                "ref": "**Official Rule:** Must not drive during acute illness. Relicensing considered after stability periods confirmed by specialist report."
            }
        }
    },
    "Chapter 5: Drug & Alcohol": {
        "url": "https://www.gov.uk/guidance/drug-or-alcohol-misuse-and-dependence-assessing-fitness-to-drive",
        "conditions": {
            "Alcohol Dependence": {
                "g1": "1 year abstinence.", "g2": "3 years abstinence.", "notif": "Yes",
                "ref": "**Official Rule:** Licence refused or revoked until 1 year of abstinence or controlled drinking has been attained."
            }
        }
    },
    "Chapter 6: Vision": {
        "url": "https://www.gov.uk/guidance/visual-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Visual Acuity": {
                "g1": "6/12 standard.", "g2": "6/7.5 standard.", "notif": "If standard not met",
                "ref": "**Official Rule:** Must read plate at 20m. Snellen 6/12 required. Group 2 requires 6/7.5 in better eye and 6/60 in poorer eye."
            }
        }
    },
    "Chapter 7: Renal & Respiratory": {
        "url": "https://www.gov.uk/guidance/renal-and-respiratory-disorders-assessing-fitness-to-drive",
        "conditions": {
            "Sleep Apnoea (OSA)": {
                "g1": "Symptom control.", "g2": "Compliance control.", "notif": "Yes",
                "ref": "**Official Rule:** Must not drive until symptoms controlled. Group 2 requires specialist review confirming CPAP compliance."
            }
        }
    },
    "Chapter 8: Miscellaneous": {
        "url": "https://www.gov.uk/guidance/miscellaneous-conditions-assessing-fitness-to-drive",
        "conditions": {
            "Post-Surgery": {
                "g1": "1-3 months.", "g2": "Occupational review.", "notif": "No",
                "ref": "**Official Rule:** No need to notify if recovery is <3 months and no other disqualifying conditions exist."
            }
        }
    }
}

# --- NAVIGATION ---
st.title("🩺 DVLA Clinical Standards 2026")
st.markdown("---")

c_chap, c_cond = st.columns(2)
with c_chap:
    sel_chap = st.selectbox("📁 Chapter / System", options=list(DVLA_DATA.keys()))
with c_cond:
    sel_cond = st.selectbox("🔬 Condition", options=list(DVLA_DATA[sel_chap]["conditions"].keys()))

# --- LINK TO SOURCE ---
st.link_button(f"🔗 View Full {sel_chap} Guidance (GOV.UK)", DVLA_DATA[sel_chap]["url"])

# --- DATA ---
res = DVLA_DATA[sel_chap]["conditions"][sel_cond]

# --- SIDEBAR CALCULATOR ---
with st.sidebar:
    st.header("⏳ Cessation Clock")
    evt_date = st.date_input("Event Date", value=date.today())
    unit = st.radio("Unit", ["Weeks", "Months"], horizontal=True)
    val = st.number_input(f"No. of {unit}", min_value=0, value=1)
    
    delta = timedelta(weeks=val) if unit == "Weeks" else timedelta(days=int(val * 30.44))
    resume = evt_date + delta
    st.metric("Resume Date", resume.strftime('%d/%m/%Y'))
    st.divider()
    st.write(f"**Condition:** {sel_cond}")
    st.write(f"**Notifiable:** {res['notif']}")

# --- MAIN DISPLAY ---
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.info(f"**🚗 Group 1 (Car/Bike)**\n\n{res['g1']}")
with col2:
    st.warning(f"**🚛 Group 2 (HGV/Bus)**\n\n{res['g2']}")

# --- LEGIBLE OFFICIAL TEXT ---
st.subheader("📖 Official Guidance Reference")
st.markdown(f"""
<div style="background-color: #f8f9fa; padding: 20px; border-left: 6px solid #005eb8; border-radius: 4px;">
    {res['ref']}
</div>
""", unsafe_allow_html=True)

# --- CLINICAL NOTE ---
st.divider()
st.subheader("🖋️ Medical Entry (Copy/Paste)")
st.code(f"DVLA FITNESS TO DRIVE ({sel_cond}): Advised {val} {unit.lower()} cessation from {evt_date.strftime('%d/%m/%Y')}. Earliest resume date: {resume.strftime('%d/%m/%Y')}. Notification required: {res['notif']}.", language="text")
