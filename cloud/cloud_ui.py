import streamlit as st
import pandas as pd

def render_cloud_section():
    # Header
    st.markdown('<div class="lvmh-tag">LVMH</div>', unsafe_allow_html=True)
    
    # Styled Container for Title
    st.markdown("""
    <div style="background:white; padding:30px; border-radius:12px; border:1px solid #eee; margin-bottom:30px;">
        <h1 style="font-family:'Playfair Display'; margin-top:0; font-size: 36px;">Cloud Storage Optimizer</h1>
        <p style="text-transform:uppercase; font-size:12px; letter-spacing:1px; color:#888; margin:0;">
            Data Lifecycle Management & Carbon ROI
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- CONFIGURATION SECTION ---
    st.markdown("### ⚙️ Configuration")
    with st.container():
        # Using columns for a dashboard feel
        c1, c2, c3, c4 = st.columns([1, 1, 1.5, 1.5])
        with c1:
            storage = st.number_input("Current Storage (TB)", value=100.0, step=10.0)
        with c2:
            region = st.text_input("AWS/Azure Region", value="eu-west-3 (Paris)")
        with c3:
            # Styled slider
            target = st.slider("Reduction Target (%)", min_value=0, max_value=100, value=30, format="%d%%")
        with c4:
            duration = st.slider("Projection Period (Years)", 1, 10, 5)

    # Context Info
    st.info("📍 **Carbon Intensity:** 58 gCO₂/kWh (France Mix) | **Data Growth Assumption:** 20% YoY")
    st.divider()

    # --- CALCULATION LOGIC (Complex Loop) ---
    data = []
    annual_growth = 0.20
    
    for i in range(duration + 1):
        # 1. BAU (Business As Usual) - No Action
        storage_bau = storage * ((1 + annual_growth) ** i)
        emissions_bau = storage_bau * 0.88 # 0.88 kgCO2/TB approx factor
        
        # 2. Optimized Scenario (Archiving Cold Data)
        # We assume we archive a percentage equal to the target
        archived_storage = storage_bau * (target / 100) if i > 0 else 0
        active_storage = storage_bau - archived_storage
        
        # Cold storage emits much less (approx 0.15 factor vs 0.88)
        emissions_opt = (active_storage * 0.88) + (archived_storage * 0.15)
        
        # 3. Compliance Check
        # Target limit is defined as BAU emissions minus the target percentage
        target_limit_emission = emissions_bau * (1 - target/100)
        
        # Is the optimized emission lower than the limit?
        is_compliant = emissions_opt <= target_limit_emission if i > 0 else True
        
        data.append({
            "Year": f"Year {i}",
            "Total Storage (TB)": f"{storage_bau:.2f}",
            "BAU Emissions (kg)": f"{emissions_bau:.0f}",
            "Data to Archive (TB)": f"{archived_storage:.2f}",
            "Optimized Emissions (kg)": f"{emissions_opt:.0f}",
            "Meets Target": "✅" if is_compliant else "❌"
        })
    
    df_res = pd.DataFrame(data)

    # --- RESULTS DISPLAY ---
    st.markdown("### 📊 Current Status vs Target")
    
    # Summary Metrics
    k1, k2, k3 = st.columns(3)
    
    final_bau = float(df_res.iloc[-1]["BAU Emissions (kg)"])
    final_opt = float(df_res.iloc[-1]["Optimized Emissions (kg)"])
    savings = final_bau - final_opt
    
    with k1:
        st.markdown(f"""
        <div style="border:1px solid #ddd; padding:15px; border-radius:8px; background:white;">
            <div style="font-size:12px; color:#666;">Target Reduction</div>
            <div style="font-size:24px; font-weight:bold;">{target}%</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div style="border:1px solid #ddd; padding:15px; border-radius:8px; background:white;">
            <div style="font-size:12px; color:#666;">Annual CO₂ Savings (Yr {duration})</div>
            <div style="font-size:24px; font-weight:bold; color: #27ae60;">{savings:.0f} kg/year</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        status = df_res.iloc[-1]["Meets Target"]
        color = "#27ae60" if status == "✅" else "#c0392b"
        msg = "Goal Achieved" if status == "✅" else "Goal Failed"
        st.markdown(f"""
        <div style="border:1px solid {color}; padding:15px; border-radius:8px; background:{color}10;">
            <div style="font-size:12px; color:#666;">Final Status</div>
            <div style="font-size:24px; font-weight:bold; color:{color};">{status} {msg}</div>
        </div>
        """, unsafe_allow_html=True)

    if df_res.iloc[-1]["Meets Target"] == "✅":
        st.success(f"✅ Great job! This archival strategy meets your CO₂ reduction targets for {duration} years.")
    else:
        st.error("❌ Warning: Increasing data volume outweighs the archival benefits in later years. Increase archival rate.")

    st.markdown("### 📅 5-Year Projection Plan")
    st.table(df_res) # Using st.table for the clean, static look seen in screenshots

    st.markdown("### 💡 Key Insights")
    st.caption("Recommendation: Implement a continuous archival policy for data older than 2 years to AWS Glacier or Azure Archive.")