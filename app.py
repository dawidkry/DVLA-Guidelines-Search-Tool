import streamlit as st
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Guidance Tool",
    page_icon="🚗",
    layout="wide"
)

# --- DATABASE ---
# Expanded data set for clinical use
DVLA_DATA = {
    "TIA / Stroke": {
        "group1": "Must not drive for 1 month. May resume after 1 month if no residual deficit. If multiple TIAs, seek specialist advice.",
        "group2": "Licence refused or revoked for 1 year. Can be relicensed after 1 year if stable and imaging is clear.",
        "notifiable": "No (unless residual deficit after 1 month)"
    },
    "Syncope (Simple Faint)": {
        "group1": "No restriction if there is an identifiable prodrome and no recurrence.",
        "group2": "No restriction unless recurring, no prodrome, or occurs while sitting/standing.",
        "notifiable": "No"
    },
    "Epilepsy (First Seizure)": {
        "group1": "Must not drive for 6 months (or 12 months if high risk). Specialist review required.",
        "group2": "Must not drive for 5 years. Must be seizure-free without medication for 10 years.",
        "notifiable": "Yes"
    },
    "Myocardial Infarction (STEMI/NSTEMI)": {
        "group1": "Must not drive for 1 week if successfully treated with primary PCI and LVEF > 40%. Otherwise 4 weeks.",
        "group2": "Must not drive for at least 6 weeks. Requires exercise test and LVEF > 40%.",
        "notifiable": "No (for Group 1)"
    },
    "Hypoglycaemia (Severe)": {
        "group1": "Must not drive if more than one episode of severe hypoglycemia in 12 months.",
        "group2": "Must not drive. Very strict criteria for relicensing.",
        "notifiable": "Yes"
    }
}

# --- STYLING (The fix is here: unsafe_allow_html) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stAlert { border-radius: 10px; }
    h1 { color: #004b87; } /* NHS Blue-ish */
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🩺 DVLA Medical Standards Quick-Reference")
st.caption(f"Logged in as: Clinician | Date: {datetime.now().strftime('%d/%m/%Y')}")

# --- SIDEBAR: Date Calculator ---
with st.sidebar:
    st.header("📅 Return to Drive Calc")
    event_date = st.date_input("Date of clinical event:", value=datetime.now())
    months_off = st.number_input("Months recommended off:", min_value=0, max_value=24, value=1)
    
    # Calculate return date
    return_date = event_date + timedelta(days=(months_off * 30))
    st.success(f"Earliest return date:\n\n**{return_date.strftime('%d %B %Y')}**")
    
    st.divider()
    st.markdown("""
    **GMC Duty of Care:**
    Doctors should advise patients of their legal requirement to notify the DVLA. If a patient continues to drive against advice, you may have a duty to disclose this to the DVLA medical adviser.
    """)

# --- MAIN SEARCH UI ---
# Search bar with a placeholder
search_input = st.text_input("Search condition (e.g. Stroke, MI, Faint):", "").strip().lower()

# Filter logic
results = {k: v for k, v in DVLA_DATA.items() if search_input in k.lower()}

if search_input and results:
    for condition, data in results.items():
        st.subheader(f"Condition: {condition}")
        
        # Notification Status
        notif_status = data['notifiable']
        color = "red" if "yes" in notif_status.lower() else "orange" if "specialist" in notif_status.lower() else "green"
        st.markdown(f"**Notifiable?** :{color}[{notif_status}]")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**🚗 Group 1 (Car/Bike)**\n\n{data['group1']}")
        with col2:
            st.warning(f"**🚛 Group 2 (Bus/Lorry)**\n\n{data['group2']}")
            
        # Discharge Summary Snippet
        st.markdown("#### 📝 Discharge Summary Text")
        snippet = f"Patient advised regarding DVLA fitness to drive standards for {condition}. Recommended driving cessation for {months_off} month(s) from date of event ({event_date.strftime('%d/%m/%Y')}). Earliest return date: {return_date.strftime('%d/%m/%Y')}. Responsibility for notification rests with the patient."
        st.code(snippet, language="text")
        st.divider()

elif search_input:
    st.error("Condition not found. Please check spelling or consult the full DVLA 'At a Glance' guide.")
else:
    st.info("Start typing a condition above to see the requirements.")

# --- FOOTER ---
st.divider()
st.caption("⚠️ **Disclaimer:** This tool is a clinical aid and does not replace the official 'Assessing fitness to drive' guidance. Ensure you verify with the latest GOV.UK updates as regulations change.")
