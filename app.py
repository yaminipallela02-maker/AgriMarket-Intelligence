import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

from voice_assistant import render_voice_assistant
from text_assistant import get_text_response
from firebase_phone import show_phone_auth

from database import (
    init_db,
    get_db_type,
    create_connection,
    get_user_by_id,
    get_user_by_phone,
    get_user_by_firebase_uid,
    create_phone_user,
    register_user,
    login_user,
    add_crop,
    get_user_crops,
    get_all_crops,
    get_latest_crop,
    delete_crop,
    add_crop_history,
    get_crop_history,
    save_prediction,
    get_predictions,
    add_transaction,
    get_transactions,
    save_profile,
    get_profile,
    seed_starter_crops_for_user
)

from price_model import (
    predict_price,
    get_monthly_predictions
)

from demand_model import (
    predict_demand,
    get_demand_level,
    get_monthly_demand_predictions
)

from crop_model import (
    recommend_crop,
    recommend_crop_scientific,
    get_crop_reason
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AgriMarket Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()

# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_phone" not in st.session_state:
    st.session_state.user_phone = ""

if "firebase_uid" not in st.session_state:
    st.session_state.firebase_uid = None

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "🏠 Home"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "🙏 నమస్కారం! అగ్రిమార్కెట్ అసిస్టెంట్ కి స్వాగతం. మీరు ఏ పంట సాగు, మండి ధరలు, తెగుళ్ళు లేదా ఎరువుల గురించి తెలుసుకోవాలనుకుంటున్నారు?"}
    ]

# --------------------------------------------------
# NAVIGATION MENU
# --------------------------------------------------

if st.session_state.logged_in:
    menu = [
        "📊 Dashboard",
        "🌱 My Crops",
        "➕ Add Crop",
        "📈 Price Prediction",
        "📊 Demand Forecasting",
        "🏪 Market Intelligence",
        "🌾 Crop Recommendation",
        "🤝 Contract Opportunities",
        "📜 Crop History",
        "💰 Transactions",
        "👤 Profile",
        "🎤 Voice Assistant",
        "💬 Text Assistant",
        "🏠 Home",
        "🚪 Logout"
    ]
else:
    menu = [
        "🏠 Home",
        "🔐 Login",
        "📝 Signup",
        "🎤 Voice Assistant",
        "💬 Text Assistant"
    ]

# Sync nav_page with menu index
if st.session_state.nav_page in menu:
    curr_idx = menu.index(st.session_state.nav_page)
else:
    curr_idx = 0
    st.session_state.nav_page = menu[0]

# Sidebar Brand
st.sidebar.title("🌾 AgriMarket")
st.sidebar.caption("Smart Farming & APMC Intelligence")

if st.session_state.logged_in:
    st.sidebar.success(f"👤 **{st.session_state.user_name}**")
    if st.session_state.user_phone:
        st.sidebar.caption(f"📱 {st.session_state.user_phone}")

# Radio navigation synced with state
selected_page = st.sidebar.radio(
    "Select Page",
    menu,
    index=curr_idx,
    key="nav_radio"
)

if selected_page != st.session_state.nav_page:
    st.session_state.nav_page = selected_page

page = st.session_state.nav_page

st.sidebar.divider()
st.sidebar.markdown(f"**Database:** `{get_db_type()}`")
st.sidebar.markdown("**ML Models:** `XGBoost & Random Forest`")
st.sidebar.markdown("**Datasets:** `Agmarknet Mandi & ICAR Ag-Science`")


# --------------------------------------------------
# 1. HOME PAGE
# --------------------------------------------------

if page == "🏠 Home":

    st.title("🌾 AgriMarket Intelligence System")
    st.subheader("AI-Powered Smart Farming, Market Intelligence & Price Forecasting")

    st.write(
        "AgriMarket Intelligence is a complete decision-support platform designed to assist farmers "
        "with real-time APMC Mandi prices, Machine Learning price & demand forecasting, scientific crop suitability recommendations, "
        "and voice-assisted multilingual market support."
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("📈 **Real Price ML**\nXGBoost model trained on real Mandi prices.")
    with col2:
        st.info("📊 **Demand Forecasting**\nPredicts seasonal mandi procurement arrivals.")
    with col3:
        st.info("🌾 **AI Recommendation**\nRandom Forest model trained on ICAR scientific soil data.")
    with col4:
        st.info("📱 **Mobile OTP & MySQL**\nSecure Firebase OTP authentication & MySQL 8.0.")

    st.divider()

    if not st.session_state.logged_in:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔐 Login with Mobile OTP", use_container_width=True):
                st.session_state.nav_page = "🔐 Login"
                st.rerun()
        with c2:
            if st.button("📝 Register New Farmer", use_container_width=True):
                st.session_state.nav_page = "📝 Signup"
                st.rerun()
    else:
        if st.button("🚀 Go to Farmer Dashboard", type="primary", use_container_width=True):
            st.session_state.nav_page = "📊 Dashboard"
            st.rerun()


# --------------------------------------------------
# 2. LOGIN PAGE (FIREBASE OTP + ONE-CLICK DEMO + EMAIL)
# --------------------------------------------------

elif page == "🔐 Login":

    st.title("🔐 Farmer Login")
    st.write("Access your farm records, ML predictions, and transactions.")
    st.divider()

    tab_otp, tab_demo, tab_email = st.tabs([
        "📱 Mobile OTP (Firebase SMS)",
        "⚡ Quick Login (Instant / Demo)",
        "📧 Email & Password"
    ])

    with tab_otp:
        st.markdown("#### 📱 Enter Mobile Number to Receive SMS OTP")
        st.caption("A 6-digit OTP will be sent directly to your phone via Firebase SMS.")

        user_data = show_phone_auth()

        if user_data:
            phone = str(user_data.get("phone", "")).strip()
            firebase_uid = str(user_data.get("uid", "")).strip()

            if phone:
                user = get_user_by_phone(phone)
                if not user and firebase_uid:
                    user = get_user_by_firebase_uid(firebase_uid)

                if not user:
                    new_user_id = create_phone_user(
                        name=f"Farmer {phone[-4:]}",
                        phone=phone,
                        firebase_uid=firebase_uid
                    )
                    user = get_user_by_id(new_user_id)

                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user["id"]
                    st.session_state.user_name = user["name"]
                    st.session_state.user_phone = user.get("phone") or phone
                    st.session_state.firebase_uid = firebase_uid
                    st.session_state.nav_page = "📊 Dashboard"
                    st.success(f"🎉 Login successful! Welcome, **{user['name']}**.")
                    st.balloons()
                    st.rerun()

    with tab_demo:
        st.markdown("#### ⚡ Quick Farmer Login (Demo & Offline Viva Mode)")
        st.info("Use this mode for instant login without waiting for SMS delivery.")

        c1, c2 = st.columns([2, 1])
        with c1:
            demo_phone = st.text_input("Farmer Mobile Number", value="+919876543210")
        with c2:
            farmer_name = st.text_input("Farmer Name", value="Yamini Farmer")

        if st.button("🚀 Instant Login to Dashboard", type="primary", use_container_width=True):
            clean_phone = demo_phone.strip()
            user = get_user_by_phone(clean_phone)
            if not user:
                uid = f"DEMO_{clean_phone.replace('+', '')}"
                new_id = create_phone_user(name=farmer_name.strip(), phone=clean_phone, firebase_uid=uid)
                user = get_user_by_id(new_id)

            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user["id"]
                st.session_state.user_name = user["name"]
                st.session_state.user_phone = user.get("phone") or clean_phone
                st.session_state.firebase_uid = user.get("firebase_uid")
                st.session_state.nav_page = "📊 Dashboard"
                st.success(f"Login successful! Welcome, {user['name']}.")
                st.rerun()

    with tab_email:
        st.markdown("#### 📧 Standard Email Login")
        email_input = st.text_input("Email Address", value="pallelayamini02@gmail.com")
        pass_input = st.text_input("Password", type="password", value="yamireddy02")

        if st.button("Login with Email", use_container_width=True):
            user_creds = login_user(email_input.strip(), pass_input.strip())
            if user_creds:
                u_id, u_name, u_email = user_creds
                u_obj = get_user_by_id(u_id)
                st.session_state.logged_in = True
                st.session_state.user_id = u_id
                st.session_state.user_name = u_name
                st.session_state.user_phone = (u_obj.get("phone") if u_obj else "") or ""
                st.session_state.nav_page = "📊 Dashboard"
                st.success(f"Welcome, {u_name}!")
                st.rerun()
            else:
                st.error("Invalid email or password.")


# --------------------------------------------------
# 3. SIGNUP PAGE
# --------------------------------------------------

elif page == "📝 Signup":

    st.title("📝 Farmer Registration")
    st.write("Register a new farming account in the AgriMarket MySQL database.")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("👤 Full Name", placeholder="e.g. Ramesh Kumar")
        new_phone = st.text_input("📱 Mobile Number", placeholder="e.g. 9876543210")
    with col2:
        new_email = st.text_input("📧 Email Address", placeholder="e.g. farmer@gmail.com")
        new_password = st.text_input("🔑 Password", type="password", placeholder="Enter password")

    if st.button("Complete Registration & Enter App", type="primary", use_container_width=True):
        if not new_name.strip() or not new_phone.strip():
            st.error("Please enter both Full Name and Mobile Number.")
        else:
            fmt_phone = new_phone.strip()
            if not fmt_phone.startswith("+") and len(fmt_phone) == 10:
                fmt_phone = "+91" + fmt_phone

            existing_phone = get_user_by_phone(fmt_phone)
            if existing_phone:
                st.warning("An account with this phone number already exists. Please log in.")
                st.session_state.nav_page = "🔐 Login"
                st.rerun()
            else:
                uid = f"USER_{fmt_phone.replace('+', '')}"
                email_val = new_email.strip() if new_email.strip() else f"farmer_{fmt_phone.replace('+', '')}@agrimarket.in"
                pwd_val = new_password.strip() if new_password.strip() else "Farmer@123"

                reg_id = register_user(
                    name=new_name.strip(),
                    email=email_val,
                    password=pwd_val,
                    phone=fmt_phone,
                    firebase_uid=uid
                )

                if reg_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = reg_id
                    st.session_state.user_name = new_name.strip()
                    st.session_state.user_phone = fmt_phone
                    st.session_state.nav_page = "📊 Dashboard"
                    st.success("🎉 Registration successful! Redirecting to Dashboard...")
                    st.rerun()
                else:
                    st.error("An account with this email already exists. Please login or choose another email.")


# --------------------------------------------------
# 4. DASHBOARD PAGE
# --------------------------------------------------

elif page == "📊 Dashboard":

    st.title("📊 Farmer Dashboard")
    st.write(f"Welcome back, **{st.session_state['user_name']}**! Here is your real-time agriculture & mandi intelligence summary.")
    st.divider()

    user_id = st.session_state["user_id"]
    crops = get_user_crops(user_id)
    transactions = get_transactions(user_id)
    predictions = get_predictions(user_id)

    total_crops = len(crops)
    total_transactions = len(transactions)

    completed_sales = [t for t in transactions if str(t.get("status")).lower() == "completed"]
    total_sales_amount = sum(float(t.get("total_amount", 0)) for t in completed_sales)

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌱 Active Crops", total_crops)
    with col2:
        st.metric("💰 Total Transactions", total_transactions)
    with col3:
        st.metric("✅ Completed Sales", len(completed_sales))
    with col4:
        st.metric("💵 Total Revenue", f"₹ {total_sales_amount:,.2f}")

    st.divider()

    col_crops, col_preds = st.columns(2)

    with col_crops:
        st.subheader("🌾 Your Cultivated Crops")
        if crops:
            for c in crops[:4]:
                with st.container(border=True):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"**🌱 {c['crop_name']}** ({c['land_area']} Acres)")
                        st.caption(f"Planting: {c.get('planting_date')} | Water: {c.get('water_source')}")
                    with c2:
                        st.markdown(f"Harvest: **{c.get('expected_harvest_date')}**")
        else:
            st.info("No crops registered yet.")

        if st.button("🌱 Manage All My Crops", key="dash_view_crops"):
            st.session_state.nav_page = "🌱 My Crops"
            st.rerun()

    with col_preds:
        st.subheader("🤖 Recent ML Intelligence Reports")
        if predictions:
            for p in predictions[:4]:
                with st.container(border=True):
                    st.markdown(f"**{p.get('prediction_type')}** — `{p.get('crop_name')}`")
                    st.caption(f"Predicted Value: ₹ {p.get('predicted_value'):,.2f} | Date: {p.get('prediction_date')}")
        else:
            st.info("No AI predictions generated yet.")

        if st.button("📈 Run Price Prediction", key="dash_run_price"):
            st.session_state.nav_page = "📈 Price Prediction"
            st.rerun()

    st.divider()
    st.subheader("⚡ Quick Shortcuts")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("➕ Add Crop", use_container_width=True):
            st.session_state.nav_page = "➕ Add Crop"
            st.rerun()
    with q2:
        if st.button("📈 Predict Price", use_container_width=True):
            st.session_state.nav_page = "📈 Price Prediction"
            st.rerun()
    with q3:
        if st.button("🏪 Mandi Intel", use_container_width=True):
            st.session_state.nav_page = "🏪 Market Intelligence"
            st.rerun()
    with q4:
        if st.button("🌾 Crop Advisor", use_container_width=True):
            st.session_state.nav_page = "🌾 Crop Recommendation"
            st.rerun()


# --------------------------------------------------
# 5. MY CROPS PAGE
# --------------------------------------------------

elif page == "🌱 My Crops":

    st.title("🌱 My Cultivated Crops")
    st.write("Manage your active crop registrations stored permanently in MySQL.")
    st.divider()

    user_id = st.session_state["user_id"]
    crops = get_user_crops(user_id)

    top_c1, top_c2, top_c3 = st.columns([2, 1, 1])
    with top_c1:
        view_mode = st.radio("Display Filter", ["My Farm Crops", "All Database Crops (Mandi Overview)"], horizontal=True)
    with top_c2:
        if st.button("➕ Add New Crop", use_container_width=True):
            st.session_state.nav_page = "➕ Add Crop"
            st.rerun()
    with top_c3:
        if st.button("🌾 Reload Demo Crops", use_container_width=True):
            seed_starter_crops_for_user(user_id)
            st.success("Refreshed standard demo crops!")
            st.rerun()

    display_crops = crops if view_mode == "My Farm Crops" else get_all_crops()

    if display_crops:
        st.markdown(f"### 📋 Showing {len(display_crops)} Registered Crops:")
        for crop in display_crops:
            farmer_label = f" (Farmer: {crop.get('farmer_name')})" if 'farmer_name' in crop else ""
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 3, 3, 2])
                with c1:
                    st.markdown(f"#### 🌱 {crop['crop_name']}{farmer_label}")
                    st.write(f"🌾 **Land Area:** `{crop['land_area']} Acres`")
                with c2:
                    st.write(f"📅 **Planting Date:** {crop['planting_date']}")
                    st.write(f"📆 **Expected Harvest:** **{crop['expected_harvest_date']}**")
                with c3:
                    st.write(f"💧 **Water Source:** {crop['water_source']}")
                    st.write(f"🧪 **Pesticide:** {crop['pesticide_usage']}")
                with c4:
                    if st.button("🗑️ Remove", key=f"del_crop_{crop['id']}", use_container_width=True):
                        delete_crop(crop['id'], user_id)
                        st.success(f"{crop['crop_name']} deleted.")
                        st.rerun()
    else:
        st.info("No crops registered. Click 'Reload Demo Crops' above to populate sample crops.")


# --------------------------------------------------
# 6. ADD CROP PAGE
# --------------------------------------------------

elif page == "➕ Add Crop":

    st.title("➕ Add New Crop Details")
    st.write("Record your crop planting details to receive AI predictions and market alerts.")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        crop_name = st.selectbox(
            "🌱 Select Crop",
            ["Rice", "Tomato", "Chilli", "Cotton", "Maize", "Groundnut", "Potato", "Onion"]
        )
        planting_date = st.date_input("📅 Planting Date", value=datetime.today())

    with col2:
        land_area = st.number_input("🌾 Land Area (Acres)", min_value=0.1, value=2.5, step=0.1)
        expected_harvest_date = st.date_input("📆 Expected Harvest Date", value=datetime.today())

    st.subheader("🌿 Irrigation & Management")
    c1, c2 = st.columns(2)
    with c1:
        water_source = st.selectbox("💧 Water Source", ["Canal", "Borewell", "Rainwater", "Drip Irrigation", "Other"])
    with c2:
        pesticide_usage = st.selectbox("🧪 Pesticide Usage", ["Low", "Medium", "High", "Organic"])

    if st.button("💾 Save Crop to MySQL Database", type="primary", use_container_width=True):
        try:
            add_crop(
                st.session_state["user_id"],
                crop_name,
                planting_date,
                land_area,
                expected_harvest_date,
                water_source,
                pesticide_usage
            )
            st.success(f"🎉 {crop_name} details successfully saved to MySQL Database!")
            st.session_state.nav_page = "🌱 My Crops"
            st.rerun()
        except Exception as err:
            st.error(f"Error saving crop: {err}")


# --------------------------------------------------
# 7. PRICE PREDICTION PAGE (REAL ML: XGBOOST)
# --------------------------------------------------

elif page == "📈 Price Prediction":

    st.title("📈 Crop Mandi Price Prediction")
    st.write("Predict future APMC mandi prices using **XGBoost Machine Learning** trained on real Agmarknet mandi records.")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        crop_name = st.selectbox(
            "Select Crop",
            ["Rice", "Tomato", "Chilli", "Cotton", "Maize", "Groundnut", "Potato", "Onion"],
            key="p_crop"
        )
        month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        month = st.selectbox(
            "Select Harvest/Selling Month",
            list(range(1, 13)),
            index=10,
            format_func=lambda num: f"Month {num} ({month_names[num-1]})",
            key="p_month"
        )

    with col2:
        land_area = st.number_input("Farm Land Area (Acres)", min_value=0.1, value=2.5, step=0.1, key="p_land")
        water_source = st.selectbox("Water Source", ["Canal", "Borewell", "Rainwater"], key="p_water")
        pesticide_usage = st.selectbox("Pesticide Usage", ["Low", "Medium", "High"], key="p_pest")

    if st.button("🔮 Run XGBoost Price Prediction", type="primary", use_container_width=True):
        try:
            with st.spinner("Executing XGBoost price regressor..."):
                pred_price_quintal = predict_price(
                    crop_name,
                    month,
                    land_area,
                    water_source,
                    pesticide_usage
                )
                pred_price_kg = pred_price_quintal / 100.0

            st.success("✅ Real ML Price Prediction Completed!")

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Predicted Price / Quintal (100 kg)", f"₹ {pred_price_quintal:,.2f}")
            with m2:
                st.metric("Estimated Price / Kg", f"₹ {pred_price_kg:,.2f}")
            with m3:
                est_total = pred_price_quintal * land_area * 15.0
                st.metric("Estimated Total Crop Value", f"₹ {est_total:,.0f}")

            save_prediction(st.session_state["user_id"], "Price Prediction", crop_name, pred_price_quintal)

            st.divider()
            st.subheader(f"📊 12-Month Price Trend Forecast for {crop_name}")
            monthly_df = get_monthly_predictions(crop_name, land_area, water_source, pesticide_usage)
            st.line_chart(monthly_df.set_index("Month")["Predicted Price"])

        except Exception as err:
            st.error(f"Price prediction error: {err}")

    st.divider()
    st.subheader("📜 Your Recent Price Predictions")
    preds = get_predictions(st.session_state["user_id"])
    price_preds = [p for p in preds if p.get("prediction_type") == "Price Prediction"]
    if price_preds:
        for p in price_preds[:5]:
            st.write(f"🌾 **{p['crop_name']}** — ₹ {p['predicted_value']:,.2f} / Quintal — Recorded on `{p['prediction_date']}`")
    else:
        st.info("No prior price predictions recorded.")


# --------------------------------------------------
# 8. DEMAND FORECASTING PAGE (REAL ML: XGBOOST)
# --------------------------------------------------

elif page == "📊 Demand Forecasting":

    st.title("📊 Crop Demand Forecasting")
    st.write("Forecast market demand volume & procurement trends using **XGBoost Regressor** ($R^2 = 0.99$).")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        crop_name = st.selectbox(
            "Select Crop",
            ["Rice", "Tomato", "Chilli", "Cotton", "Maize", "Groundnut", "Potato", "Onion"],
            key="d_crop"
        )
        month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        month = st.selectbox(
            "Select Target Month",
            list(range(1, 13)),
            index=10,
            format_func=lambda num: f"Month {num} ({month_names[num-1]})",
            key="d_month"
        )

    with col2:
        land_area = st.number_input("Land Area (Acres)", min_value=0.1, value=3.0, step=0.1, key="d_land")
        water_source = st.selectbox("Water Source", ["Canal", "Borewell", "Rainwater"], key="d_water")

    if st.button("🔮 Forecast Market Demand", type="primary", use_container_width=True):
        try:
            with st.spinner("Analyzing seasonal demand patterns..."):
                dem_val = predict_demand(crop_name, month, land_area, water_source)
                dem_level = get_demand_level(dem_val)

            st.success("✅ Demand Forecast Generated!")

            c1, c2 = st.columns(2)
            with c1:
                st.metric("Predicted Market Arrival Demand", f"{dem_val:,.1f} Quintals/day")
            with c2:
                st.metric("Demand Status", dem_level)

            save_prediction(st.session_state["user_id"], "Demand Prediction", crop_name, dem_val)

            st.divider()
            st.subheader(f"📈 12-Month Demand Curve for {crop_name}")
            monthly_dem = get_monthly_demand_predictions(crop_name, land_area, water_source)
            st.line_chart(monthly_dem.set_index("Month")["Predicted Demand"])

        except Exception as err:
            st.error(f"Demand forecasting error: {err}")


# --------------------------------------------------
# 9. MARKET INTELLIGENCE PAGE (REAL MANDI DATASET)
# --------------------------------------------------

elif page == "🏪 Market Intelligence":

    st.title("🏪 Real APMC Market Intelligence")
    st.write("Compare real APMC mandi prices and find the highest paying markets across India from the government dataset (6,687 records).")
    st.divider()

    selected_crop = st.selectbox(
        "🌱 Select Commodity",
        ["Rice", "Tomato", "Chilli", "Cotton", "Maize", "Groundnut", "Potato", "Onion"]
    )

    csv_path = Path(__file__).resolve().parent / "data" / "mandi_prices_cleaned.csv"
    if csv_path.exists():
        df_mandi = pd.read_csv(csv_path)
        df_mandi.columns = df_mandi.columns.str.strip().str.replace("_x0020_", "_", regex=False)

        crop_filter = df_mandi["Commodity"].str.contains(selected_crop, case=False, na=False)
        if selected_crop == "Rice":
            crop_filter = df_mandi["Commodity"].str.contains("Rice|Paddy", case=False, na=False)
        elif selected_crop == "Chilli":
            crop_filter = df_mandi["Commodity"].str.contains("Chilli|Chili", case=False, na=False)

        matched_df = df_mandi[crop_filter].dropna(subset=["Modal_Price"]).copy()

        if not matched_df.empty:
            matched_df["Modal_Price"] = pd.to_numeric(matched_df["Modal_Price"], errors="coerce")
            matched_df = matched_df.sort_values(by="Modal_Price", ascending=False)

            best_row = matched_df.iloc[0]

            st.subheader("🏆 Top Paying Market for " + selected_crop)
            b1, b2, b3 = st.columns(3)
            with b1:
                st.metric("Best Market", best_row.get("Market", "APMC"))
                st.caption(f"State: {best_row.get('State')} | District: {best_row.get('District')}")
            with b2:
                st.metric("Modal Price (Quintal)", f"₹ {best_row.get('Modal_Price'):,.2f}")
            with b3:
                st.metric("Price per Kg", f"₹ {best_row.get('Modal_Price')/100.0:,.2f}")

            st.divider()
            st.subheader(f"📊 Live Market Price Comparison ({selected_crop})")

            top_markets = matched_df.head(8)[["State", "District", "Market", "Min_Price", "Max_Price", "Modal_Price"]]
            st.dataframe(top_markets, use_container_width=True)

            st.subheader("📈 Market Price Comparison Chart (₹ / Quintal)")
            chart_df = top_markets.copy()
            chart_df["Market_Label"] = chart_df["Market"] + " (" + chart_df["District"] + ")"
            st.bar_chart(chart_df.set_index("Market_Label")["Modal_Price"])
        else:
            st.info(f"No active market transactions found for {selected_crop} in recent dataset.")


# --------------------------------------------------
# 10. CROP RECOMMENDATION PAGE (REAL SCIENTIFIC ML)
# --------------------------------------------------

elif page == "🌾 Crop Recommendation":

    st.title("🌾 AI Crop Recommendation System")
    st.write("Scientific crop suitability analysis powered by **Random Forest Machine Learning** trained on 2,700 ICAR/Kaggle agro-climatic records (94.8% Accuracy).")
    st.divider()

    tab_sci, tab_farm = st.tabs([
        "🧪 Scientific Soil & Climate Mode (N-P-K & Weather)",
        "🌾 Simple Farm Condition Mode"
    ])

    with tab_sci:
        st.markdown("#### 🧪 Enter Soil Chemical Nutrients & Climatic Data")
        s_c1, s_c2 = st.columns(2)
        with s_c1:
            inp_n = st.slider("Nitrogen (N) Content in Soil", min_value=0.0, max_value=140.0, value=80.0, step=1.0)
            inp_p = st.slider("Phosphorus (P) Content in Soil", min_value=5.0, max_value=145.0, value=50.0, step=1.0)
            inp_k = st.slider("Potassium (K) Content in Soil", min_value=5.0, max_value=205.0, value=40.0, step=1.0)
            inp_ph = st.slider("Soil pH Level", min_value=4.0, max_value=9.0, value=6.5, step=0.1)
        with s_c2:
            inp_temp = st.number_input("Average Temperature (°C)", min_value=10.0, max_value=45.0, value=25.5, step=0.5)
            inp_hum = st.slider("Relative Humidity (%)", min_value=15.0, max_value=100.0, value=80.0, step=1.0)
            inp_rain = st.number_input("Rainfall (mm)", min_value=20.0, max_value=300.0, value=200.0, step=5.0)

        if st.button("🔬 Run Scientific Crop Recommendation", type="primary", use_container_width=True):
            try:
                rec_crop, conf = recommend_crop_scientific(inp_n, inp_p, inp_k, inp_temp, inp_hum, inp_ph, inp_rain)
                st.success("✅ Scientific Analysis Completed!")
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown(f"### 🌾 Recommended Crop: **{rec_crop}**")
                    st.metric("Model Confidence Score", f"{conf:.2f}%")
                with r2:
                    st.markdown("### 📋 Agronomic Justification")
                    st.info(get_crop_reason(rec_crop))
                save_prediction(st.session_state["user_id"], "Crop Recommendation", rec_crop, conf)
            except Exception as err:
                st.error(f"Error: {err}")

    with tab_farm:
        st.markdown("#### 🌾 High-Level Farm Profile Recommendation")
        col1, col2 = st.columns(2)
        with col1:
            soil_type = st.selectbox("🌱 Soil Type", ["Clay", "Loamy", "Sandy", "Black"])
            water_availability = st.selectbox("💧 Water Availability", ["High", "Medium", "Low"])
        with col2:
            climate = st.selectbox("🌤️ Climate Condition", ["Hot", "Warm", "Cool", "Humid", "Dry"])
            land_area = st.number_input("🌾 Land Area (Acres)", min_value=0.1, value=3.0, step=0.1)

        if st.button("🤖 Recommend Crop based on Farm Profile", type="primary", use_container_width=True):
            try:
                recommended, confidence = recommend_crop(soil_type, water_availability, land_area, climate)
                st.success("✅ AI Crop Evaluation Completed!")
                res_c1, res_c2 = st.columns(2)
                with res_c1:
                    st.markdown(f"### 🌾 Recommended Crop: **{recommended}**")
                    st.metric("Model Confidence Score", f"{confidence:.2f}%")
                with res_c2:
                    st.markdown("### 📋 Agronomic Justification")
                    st.info(get_crop_reason(recommended))
                save_prediction(st.session_state["user_id"], "Crop Recommendation", recommended, confidence)
            except Exception as err:
                st.error(f"Recommendation error: {err}")


# --------------------------------------------------
# 11. CONTRACT OPPORTUNITIES PAGE
# --------------------------------------------------

elif page == "🤝 Contract Opportunities":

    st.title("🤝 Corporate & Contract Farming Connect")
    st.write("Connect directly with agribusinesses, food processors, and wholesale buyers.")
    st.divider()

    crop_sel = st.selectbox(
        "Select Crop for Buyers",
        ["Rice", "Tomato", "Chilli", "Cotton", "Maize", "Groundnut", "Potato", "Onion"]
    )

    contracts = [
        {"Company": "ITC Agri Business", "Requirement": "500 Quintals", "Offered Price": "₹ 2,900 / Qtl", "Location": "Guntur / Vijayawada", "Contact": "procurement@itc.in"},
        {"Company": "Reliance Retail Fresh", "Requirement": "250 Quintals", "Offered Price": "₹ 3,100 / Qtl", "Location": "Krishna / Eluru", "Contact": "agro@ril.com"},
        {"Company": "Godrej Agrovet", "Requirement": "400 Quintals", "Offered Price": "₹ 2,850 / Qtl", "Location": "Andhra Pradesh", "Contact": "buy@godrejagrovet.com"}
    ]

    for con in contracts:
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**🏢 {con['Company']}**")
                st.write(f"Seeking: `{crop_sel}` ({con['Requirement']})")
            with c2:
                st.metric("Offered Price", con["Offered Price"])
                st.caption(f"Hub: {con['Location']}")
            with c3:
                st.write(f"Email: {con['Contact']}")
                if st.button("Apply for Contract", key=con["Company"]):
                    st.success(f"Application sent to {con['Company']} for {crop_sel}!")


# --------------------------------------------------
# 12. CROP HISTORY PAGE
# --------------------------------------------------

elif page == "📜 Crop History":

    st.title("📜 Historical Harvest Records")
    st.write("Maintain your past harvest logs and yield data in MySQL.")
    st.divider()

    with st.expander("➕ Log Past Harvest Record"):
        h_crop = st.selectbox("Crop Name", ["Rice", "Tomato", "Chilli", "Cotton", "Maize", "Groundnut", "Potato", "Onion"], key="h_c")
        h_qty = st.number_input("Quantity Produced (Quintals)", min_value=1.0, value=25.0)
        h_date = st.date_input("Harvest Date", value=datetime.today())
        if st.button("Save Harvest Log"):
            add_crop_history(st.session_state["user_id"], h_crop, h_qty, str(h_date))
            st.success("Harvest record saved.")
            st.rerun()

    history = get_crop_history(st.session_state["user_id"])
    if history:
        for item in history:
            with st.container(border=True):
                st.markdown(f"🌾 **{item['crop_name']}** — Quantity: **{item['quantity']} Quintals**")
                st.caption(f"Harvest Date: {item.get('harvest_date')}")
    else:
        st.info("No past harvest records found.")


# --------------------------------------------------
# 13. TRANSACTIONS PAGE
# --------------------------------------------------

elif page == "💰 Transactions":

    st.title("💰 Sales & Financial Transactions")
    st.write("Track sales, payments, buyers, and farm revenue stored in MySQL.")
    st.divider()

    with st.expander("➕ Record New Crop Sale", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            t_crop = st.selectbox("Crop Sold", ["Rice", "Tomato", "Chilli", "Cotton", "Maize", "Groundnut", "Potato", "Onion"])
            t_buyer = st.text_input("Buyer / Trader Name", placeholder="e.g. Sri Krishna Traders")
            t_qty = st.number_input("Quantity (Quintals)", min_value=1.0, value=20.0)
        with c2:
            t_price = st.number_input("Price per Unit (₹)", min_value=1.0, value=2600.0)
            t_status = st.selectbox("Payment Status", ["Completed", "Pending", "Cancelled"])
            total_calc = t_qty * t_price
            st.metric("Total Sale Amount", f"₹ {total_calc:,.2f}")

        if st.button("💾 Save Transaction to MySQL", type="primary"):
            if not t_buyer.strip():
                st.error("Please enter the buyer name.")
            else:
                add_transaction(st.session_state["user_id"], t_crop, t_buyer.strip(), t_qty, t_price, t_status)
                st.success("Transaction recorded successfully!")
                st.rerun()

    trans = get_transactions(st.session_state["user_id"])
    if trans:
        st.subheader("📜 Recent Transactions")
        for t in trans:
            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**🌾 {t['crop_name']}** ➔ {t['buyer_name']}")
                    st.caption(f"Date: {t.get('transaction_date')}")
                with c2:
                    st.markdown(f"Qty: **{t['quantity']}** Qtl @ **₹ {t['price']}**")
                    st.caption(f"Total: ₹ {t['total_amount']:,.2f}")
                with c3:
                    st.write(f"Status: **{t['status']}**")
    else:
        st.info("No sales transactions recorded yet.")


# --------------------------------------------------
# 14. PROFILE PAGE
# --------------------------------------------------

elif page == "👤 Profile":

    st.title("👤 Farmer Profile")
    st.write("View and update your personal, regional, and farm profile in MySQL.")
    st.divider()

    user_id = st.session_state["user_id"]
    profile = get_profile(user_id) or {}

    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Full Name", value=st.session_state["user_name"], disabled=True)
        phone_val = st.text_input("Mobile Number", value=profile.get("phone") or st.session_state.get("user_phone", ""))
        location_val = st.text_input("Location / Region", value=profile.get("location") or "Andhra Pradesh")
        village_val = st.text_input("Village", value=profile.get("village") or "")

    with c2:
        district_val = st.text_input("District", value=profile.get("district") or "Krishna")
        state_val = st.text_input("State", value=profile.get("state") or "Andhra Pradesh")
        area_val = st.number_input("Total Farm Land (Acres)", min_value=0.1, value=float(profile.get("land_area") or 2.5), step=0.1)

    if st.button("💾 Save Profile Details", type="primary"):
        save_profile(user_id, phone_val, location_val, village_val, district_val, state_val, area_val)
        st.success("Profile updated successfully in MySQL!")
        st.session_state.user_phone = phone_val
        st.rerun()


# --------------------------------------------------
# 15. VOICE ASSISTANT PAGE
# --------------------------------------------------

elif page == "🎤 Voice Assistant":

    st.title("🎤 AgriMarket Multilingual Voice Assistant")
    st.write("Speak in **Telugu** or **English** to ask about crop prices, farming advice, and mandi trends.")
    st.divider()

    render_voice_assistant()


# --------------------------------------------------
# 16. TEXT ASSISTANT PAGE (INTERACTIVE AGRI-BOT CHAT)
# --------------------------------------------------

elif page == "💬 Text Assistant":

    st.title("💬 AgriMarket Intelligent Chat Assistant")
    st.write("Ask any question regarding Mandi prices, crop cultivation, pests, fertilizers, and farming in **Telugu**, **English**, or **Tanglish**.")
    st.divider()

    col_lang, col_clear = st.columns([3, 1])
    with col_lang:
        lang_choice = st.radio("Choose Output Language / సమాధాన భాష", ["Telugu", "English"], horizontal=True)
    with col_clear:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "నమస్కారం! అగ్రిమార్కెట్ చాట్ అసిస్టెంట్ కి స్వాగతం. మీ ప్రశ్నను అడగండి." if lang_choice == "Telugu" else "Hello! Welcome to AgriMarket Chat Assistant. Ask your farming or mandi question."}
            ]
            st.rerun()

    st.markdown("#### 💡 Quick Questions (ఒక క్లిక్‌తో తక్షణ సమాధానం పొందండి):")
    p1, p2, p3, p4 = st.columns(4)
    quick_query = None

    if lang_choice == "Telugu":
        with p1:
            if st.button("🍅 టమాటా మార్కెట్ ధర", use_container_width=True): quick_query = "టమాటా తాజా మార్కెట్ ధర ఎంత?"
        with p2:
            if st.button("🌾 వరి ఎరువుల మోతాదు", use_container_width=True): quick_query = "వరి పంటలో ఎరువుల మోతాదు ఏమిటి?"
        with p3:
            if st.button("🌶️ మిర్చి తామర పురుగులు", use_container_width=True): quick_query = "మిర్చిలో నల్ల తామర పురుగుల నివారణ"
        with p4:
            if st.button("🏛️ రైతు ప్రభుత్వ పథకాలు", use_container_width=True): quick_query = "రైతులకు ప్రభుత్వ పథకాలు ఏమిటి?"
    else:
        with p1:
            if st.button("🍅 Tomato Mandi Price", use_container_width=True): quick_query = "Tomato live mandi price in APMC"
        with p2:
            if st.button("🌾 Rice Fertilizer Guide", use_container_width=True): quick_query = "What fertilizer dose for rice crop?"
        with p3:
            if st.button("🌶️ Chilli Pest Management", use_container_width=True): quick_query = "How to control chilli thrips and mites?"
        with p4:
            if st.button("🏛️ PM-KISAN Scheme", use_container_width=True): quick_query = "PM Kisan and government schemes for farmers"

    # Display Conversation History
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Handle quick query clicked
    if quick_query:
        st.session_state.chat_history.append({"role": "user", "content": quick_query})
        with st.chat_message("user"):
            st.markdown(quick_query)

        with st.spinner("Analyzing agricultural intelligence..."):
            ans = get_text_response(quick_query, lang_choice)

        st.session_state.chat_history.append({"role": "assistant", "content": ans})
        with st.chat_message("assistant"):
            st.markdown(ans)
        st.rerun()

    # User chat input box (Enter key or Send button works instantly!)
    user_prompt = st.chat_input("Type your farming question here / మీ ప్రశ్నను ఇక్కడ టైప్ చేయండి (ఉదా: 'వరి ధర ఎంత?', 'tamata rate', 'chilli pests')...")
    if user_prompt:
        # Add user message to state
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Generate response
        with st.spinner("Analyzing agricultural intelligence..."):
            answer = get_text_response(user_prompt, lang_choice)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.rerun()


# --------------------------------------------------
# 17. LOGOUT
# --------------------------------------------------

elif page == "🚪 Logout":

    st.title("🚪 Logout")
    st.write("Are you sure you want to end your farming session?")

    if st.button("Confirm Logout", type="primary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = ""
        st.session_state.user_phone = ""
        st.session_state.firebase_uid = None
        st.session_state.nav_page = "🏠 Home"
        st.success("You have been logged out.")
        st.rerun()
