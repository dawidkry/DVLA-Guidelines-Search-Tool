import streamlit as st
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DVLA Clinical Guidance Tool",
    page_icon="🚗",
    layout="wide"
)

# --- DATABASE (Mock Data for Prototype) ---
# In a full version, we could scrape the GOV.UK HTML, 
# but for speed, we'll use a structured dictionary.
DVLA_DATA = {
    "TIA / Stroke": {
        "group1": "Must not drive for 1 month. May resume after 1 month if no residual deficit.",
        "group2": "Licence refused or revoked for 1 year. Can be relicensed after 1 year if stable.",
        "notifiable": "Only if multiple TIAs over short period or residual deficit after 1 month."
    },
    "Syncope (Simple Faint)": {
        "group1": "No restriction if there is an identifiable prodrome and no recurrence.",
        "group2": "No restriction unless recurring or no prodrome.",
        "notifiable": "No."
    },
    "Epilepsy (First Seizure)": {
        "group1": "Must not drive for 6 months or 12 months depending on risk factors.",
        "group2": "Must not drive for 5 years. Must be seizure-free without medication for 10 years.",
        "notifiable": "Yes."
    },
    "Myocardial Infarction (STEMI/NSTEMI)": {
        "group1": "Must not drive for 1 week if successfully treated with primary PCI.",
        "group2": "Must not drive for at least 6 weeks. Requires LVEF > 40%.",
        "notifiable": "No (for Group 1)."
    }
}

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_info=True)

# --- HEADER ---
st.title("🩺 DVLA Medical Standards Quick-Reference")
st.caption("A clinician-focused tool for rapid fitness-to-drive assessment during discharge or clinic.")

# --- SIDEBAR (Calculator & Info) ---
with st.sidebar:
    st.header("📅 Return to Drive Calc")
    event_date = st.date_input("Date of clinical event:", value=datetime.now())
    months_off = st.number_input("Months recommended off:", min_value=0, max_value=24, value=1)
    
    # Calculate return date
    # Note: Using 30 days per month for clinical estimation
    return_date = event_date + timedelta(days=(months_off * 30))
    st.success(f"Earliest return date:\n\n**{return_date.strftime('%d %B %Y')}**")
    
    st.divider()
    st.info("📞 **DVLA Medical Advisory**\n\n01792 782337\n(Mon-Fri, 10:30am - 1:00pm)")

# --- MAIN SEARCH UI ---
search_query = st.selectbox(
    "Search Medical Condition:",
    options=["Select a condition..."] + list(DVLA_DATA.keys())
)

if search_query != "Select a condition...":
    data = DVLA_DATA[search_query]
    
    # Notification Status Row
    notif_color = "red" if data['notifiable'].lower() == "yes" else "green"
    st.markdown(f"### **Notifiable to DVLA?** <span style='color:{notif_color}'>{data['notifiable']}</span>", unsafe_allow_html=True)
    
    # Comparison Columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚗 Group 1")
        st.caption("Cars and Motorcycles")
        st.info(data['group1'])
        
    with col2:
        st.subheader("🚛 Group 2")
        st.caption("Lorries and Buses")
        st.warning(data['group2'])
        
    # Discharge Summary Snippet
    st.divider()
    st.subheader("📝 Discharge Summary Text (Copy/Paste)")
    snippet = f"Following your {search_query}, you have been advised that you must not drive for {months_off} month(s). Based on current DVLA guidance, your earliest date to resume driving is {return_date.strftime('%d/%m/%Y')}. It is your legal responsibility to notify the DVLA if required."
    st.text_area("Patient Advice:", value=snippet, height=100)

else:
    st.write("Please select a condition from the dropdown above to see the specific DVLA requirements.")

# --- FOOTER / DISCLAIMER ---
st.divider()
st.caption("⚠️ **Disclaimer:** This tool is for educational purposes only and should be cross-referenced with the latest version of 'Assessing fitness to drive: a guide for medical professionals' on GOV.UK. Clinical judgment remains paramount.")
