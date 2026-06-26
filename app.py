import streamlit as st
import pandas as pd
from datetime import datetime
import database as db

# Page Configuration
st.set_page_config(
    page_title="MAHAVEER AUTO SHINER",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize Database
db.init_db()

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "edit_customer_id" not in st.session_state:
    st.session_state.edit_customer_id = None
if "log_visit_customer_id" not in st.session_state:
    st.session_state.log_visit_customer_id = None

# Gatekeeper check
if not st.session_state.logged_in:
    import auth
    auth.show_login_page()
    st.stop()


# Custom CSS for modern design and mobile friendliness
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Font style */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Main Title Styling */
    .main-title {
        font-size: 2.6rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
        letter-spacing: -0.5px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Card Styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem 1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    .metric-card:hover {
        transform: translateY(-3px);
    }
    .metric-customers:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.15);
    }
    .metric-vehicles:hover {
        border-color: rgba(168, 85, 247, 0.4);
        box-shadow: 0 10px 25px rgba(168, 85, 247, 0.15);
    }
    .metric-collections:hover {
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.15);
    }
    .metric-pending:hover {
        border-color: rgba(239, 68, 68, 0.4);
        box-shadow: 0 10px 25px rgba(239, 68, 68, 0.15);
    }
    
    .font-blue { color: #6366f1 !important; font-size: 2.2rem; font-weight: 700; }
    .font-purple { color: #a855f7 !important; font-size: 2.2rem; font-weight: 700; }
    .font-green { color: #10b981 !important; font-size: 2.2rem; font-weight: 700; }
    .font-red { color: #ef4444 !important; font-size: 2.2rem; font-weight: 700; }
    
    .metric-lbl {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-top: 0.25rem;
    }

    /* License Plate styling */
    .license-plate {
        background-color: #fcd34d;
        color: #0f172a;
        font-family: 'Courier New', Courier, monospace;
        font-weight: 800;
        padding: 3px 8px;
        border-radius: 5px;
        border: 2px solid #1e293b;
        display: inline-block;
        letter-spacing: 1px;
        font-size: 0.85rem;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.15);
        margin-right: 8px;
    }

    /* Target Streamlit native containers Styled as Glassmorphic Cards */
    div[data-testid="element-container"] div[data-testid="stVerticalBlockBorder"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="element-container"] div[data-testid="stVerticalBlockBorder"]:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.1) !important;
    }

    /* Custom buttons and actions */
    .stButton>button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #a855f7) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4f46e5, #9333ea) !important;
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Make forms stand out */
    .stForm {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        background-color: rgba(255, 255, 255, 0.01) !important;
    }

    /* Input elements styling */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
    }

    /* Tabs Styling */
    div[data-testid="stTabBar"] {
        background-color: rgba(255, 255, 255, 0.01) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        margin-bottom: 20px !important;
    }
    button[data-testid="stMarkdownContainer"] {
        font-weight: 600 !important;
    }

    /* Mobile optimization */
    @media (max-width: 640px) {
        .main-title {
            font-size: 2rem;
        }
        .sub-title {
            font-size: 0.95rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load data
def load_data():
    records = db.get_all_customers()
    if not records:
        return pd.DataFrame(columns=[
            "ID", "Customer Name", "Vehicle Number", 
            "Vehicle Model", "Vehicle Color", "Bill Number(s)",
            "Coating Date", "Free Buffing Date", "Total Amount"
        ])
    
    df = pd.DataFrame(records)
    # Rename columns for presentation
    df = df.rename(columns={
        "id": "ID",
        "customer_name": "Customer Name",
        "vehicle_number": "Vehicle Number",
        "vehicle_model": "Vehicle Model",
        "vehicle_color": "Vehicle Color",
        "coating_dates": "Coating Date",
        "free_buffing_date": "Free Buffing Date",
        "total_amount": "Total Amount",
        "bill_numbers": "Bill Number(s)",
        "buffing_date": "Buffing DateSort" # Used internally for sorting
    })
    return df

# User status and logout row
logout_col1, logout_col2 = st.columns([3, 1])
with logout_col1:
    st.markdown(f"👤 Logged in as: **{st.session_state.username}** (`{st.session_state.user_role}`)")
with logout_col2:
    if st.button("🚪 Logout", use_container_width=True):
        import auth
        auth.logout_user()

st.markdown("---")

# Main Header
st.markdown('<div class="main-title">✨ MAHAVEER AUTO SHINER</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Simple & Mobile-Friendly Coating Records Management</div>', unsafe_allow_html=True)

# Load Records
df_records = load_data()

# Fetch dynamic options from database merged with defaults
default_models = ["ACTIVA", "ACTIVA 125", "SP125", "SHINE125", "SHINE100", "UNICORN", "X-BLADE", "HORNET 150", "DIO"]
db_models = db.get_unique_models()
all_models = list(dict.fromkeys(default_models + [m.upper() for m in db_models if m]))

default_colors = ["WHITE", "BLACK", "PS BLUE", "COPPER", "GREY", "RED"]
db_colors = db.get_unique_colors()
all_colors = list(dict.fromkeys(default_colors + [c.upper() for c in db_colors if c]))

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard & Search", "➕ Add Customer", "🔁 Log Return Visit", "⚙️ Manage Records"])

# ================= TAB 1: DASHBOARD & SEARCH =================
with tab1:
    # Inline Edit Profile Container
    if st.session_state.edit_customer_id is not None:
        edit_id = st.session_state.edit_customer_id
        # Find the customer profile
        cust_row = df_records[df_records["ID"] == edit_id]
        if not cust_row.empty:
            cust_data = cust_row.iloc[0]
            cust_name_val = cust_data["Customer Name"] if cust_data["Customer Name"] else "*(No Name)*"
            st.markdown(f"### ✏️ Edit Profile for {cust_name_val} ({cust_data['Vehicle Number']})")
            with st.form("inline_edit_form"):
                edit_name = st.text_input("Customer Name (Optional)", value=cust_data["Customer Name"] if cust_data["Customer Name"] else "")
                edit_v_num = st.text_input("Vehicle Number*", value=cust_data["Vehicle Number"]).upper().strip()
                
                # Model selection logic
                curr_model = cust_data["Vehicle Model"].upper().strip() if cust_data["Vehicle Model"] else ""
                options_models = all_models.copy()
                if curr_model and curr_model not in options_models:
                    options_models.append(curr_model)
                
                edit_v_model = st.selectbox(
                    "Vehicle Model*",
                    options=options_models,
                    index=options_models.index(curr_model) if curr_model in options_models else None,
                    placeholder="Select or type model...",
                    accept_new_options=True,
                    key="edit_v_model_sel_inline"
                )

                # Color selection logic
                curr_color = cust_data["Vehicle Color"].upper().strip() if cust_data["Vehicle Color"] else ""
                options_colors = all_colors.copy()
                if curr_color and curr_color not in options_colors:
                    options_colors.append(curr_color)
                
                edit_v_color = st.selectbox(
                    "Vehicle Color*",
                    options=options_colors,
                    index=options_colors.index(curr_color) if curr_color in options_colors else None,
                    placeholder="Select or type color...",
                    accept_new_options=True,
                    key="edit_v_color_sel_inline"
                )
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    save_btn = st.form_submit_button("💾 Save Profile", use_container_width=True)
                    if save_btn:
                        edit_v_model_str = edit_v_model.strip().upper() if edit_v_model else ""
                        edit_v_color_str = edit_v_color.strip().upper() if edit_v_color else ""
                        
                        if not edit_v_num.strip():
                            st.error("Vehicle Number is required.")
                        elif not edit_v_model_str:
                            st.error("Vehicle Model is required.")
                        elif not edit_v_color_str:
                            st.error("Vehicle Color is required.")
                        else:
                            success, msg = db.update_customer(
                                edit_id,
                                edit_name.strip() if edit_name.strip() else None,
                                edit_v_num,
                                edit_v_model_str,
                                edit_v_color_str
                            )
                            if success:
                                st.success("Customer profile updated successfully!")
                                st.session_state.edit_customer_id = None
                                st.rerun()
                            else:
                                st.error(f"Error: {msg}")
                with col_cancel:
                    cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)
                    if cancel_btn:
                        st.session_state.edit_customer_id = None
                        st.rerun()
            st.markdown("---")

    # Inline Log Return Visit Container
    elif st.session_state.log_visit_customer_id is not None:
        visit_cust_id = st.session_state.log_visit_customer_id
        cust_row = df_records[df_records["ID"] == visit_cust_id]
        if not cust_row.empty:
            cust_data = cust_row.iloc[0]
            cust_name_lbl = cust_data['Customer Name'] if cust_data['Customer Name'] else "*(No Name)*"
            st.markdown(f"### 🔁 Log Return Coating Visit")
            st.markdown(f"Logging return visit for **{cust_name_lbl}** ({cust_data['Vehicle Number']})")
            with st.form("inline_visit_form"):
                return_bill = st.text_input("Bill Number (Optional)", placeholder="e.g. B-102", key="inline_return_bill")
                return_date = st.date_input("Coating Date*", value=datetime.today(), key="inline_return_date")
                return_amount = st.number_input("Payment Amount (₹)*", min_value=0.0, value=0.0, step=50.0, key="inline_return_amount")
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    save_visit = st.form_submit_button("💾 Log Coating Visit", use_container_width=True)
                    if save_visit:
                        formatted_return_date = return_date.strftime("%Y-%m-%d")
                        bill_no_val = return_bill.strip() if return_bill.strip() else None
                        status_val = "Paid" if return_amount > 0.0 else "Pending"
                        success, msg = db.add_visit(
                            visit_cust_id,
                            formatted_return_date,
                            return_amount,
                            status_val,
                            bill_no_val
                        )
                        if success:
                            st.success("Coating visit logged successfully!")
                            st.session_state.log_visit_customer_id = None
                            st.rerun()
                        else:
                            st.error(f"Error: {msg}")
                with col_cancel:
                    cancel_visit = st.form_submit_button("❌ Cancel", use_container_width=True)
                    if cancel_visit:
                        st.session_state.log_visit_customer_id = None
                        st.rerun()
            st.markdown("---")

    # Top Stats Calculation from Database Helper
    total_customers, total_vehicles, total_collections, pending_count = db.get_stats()

    # Layout for Metrics Grid
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card metric-customers">
            <div class="metric-val font-blue">{total_customers}</div>
            <div class="metric-lbl">Total Customers</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card metric-vehicles">
            <div class="metric-val font-purple">{total_vehicles}</div>
            <div class="metric-lbl">Total Vehicles</div>
        </div>
        """, unsafe_allow_html=True)
        
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="metric-card metric-collections">
            <div class="metric-val font-green">₹{total_collections:,.2f}</div>
            <div class="metric-lbl">Total Collections</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card metric-pending">
            <div class="metric-val font-red">{pending_count}</div>
            <div class="metric-lbl">Pending Payments</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Search and Filter
    st.subheader("🔍 Search & Filter")
    search_col1, search_col2 = st.columns([2, 1])
    
    with search_col1:
        search_query = st.text_input("Search records", placeholder="Enter name, vehicle number, or bill number...").strip()
    
    with search_col2:
        sort_by = st.selectbox(
            "Sort by", 
            ["Name (A-Z)", "Name (Z-A)", "Vehicle Number (A-Z)", "Vehicle Number (Z-A)", "Free Buffing Date (Newest First)", "Free Buffing Date (Oldest First)"]
        )
    
    # Filter and Sort Data
    filtered_df = df_records.copy()
    
    if search_query:
        # Search by Customer Name, Vehicle Number, or Bill Number
        filtered_df = filtered_df[
            filtered_df["Customer Name"].str.contains(search_query, case=False, na=False) |
            filtered_df["Vehicle Number"].str.contains(search_query, case=False, na=False) |
            filtered_df["Bill Number(s)"].str.contains(search_query, case=False, na=False)
        ]
        
    # Apply Sorting
    if not filtered_df.empty:
        if sort_by == "Name (A-Z)":
            filtered_df = filtered_df.sort_values(by="Customer Name", ascending=True)
        elif sort_by == "Name (Z-A)":
            filtered_df = filtered_df.sort_values(by="Customer Name", ascending=False)
        elif sort_by == "Vehicle Number (A-Z)":
            filtered_df = filtered_df.sort_values(by="Vehicle Number", ascending=True)
        elif sort_by == "Vehicle Number (Z-A)":
            filtered_df = filtered_df.sort_values(by="Vehicle Number", ascending=False)
        elif sort_by == "Free Buffing Date (Newest First)":
            filtered_df = filtered_df.sort_values(by="Buffing DateSort", ascending=False)
        elif sort_by == "Free Buffing Date (Oldest First)":
            filtered_df = filtered_df.sort_values(by="Buffing DateSort", ascending=True)

    # Display Records
    st.subheader(f"Records ({len(filtered_df)})")
    if filtered_df.empty:
        st.info("No records found.")
    else:
        # Define display columns to exclude internal sorting key
        cols_to_show = ["ID", "Customer Name", "Vehicle Number", "Vehicle Model", "Vehicle Color", "Bill Number(s)", "Coating Date", "Free Buffing Date", "Total Amount"]
        
        # Fill NaN values in Customer Name with empty string for cleaner display
        display_df = filtered_df.copy()
        display_df["Customer Name"] = display_df["Customer Name"].fillna("")
        
        # Toggle view mode
        view_mode = st.radio("Display View", ["📇 Modern Cards", "📊 Data Table"], horizontal=True, key="view_mode_toggle")
        
        if view_mode == "📊 Data Table":
            st.dataframe(display_df[cols_to_show], use_container_width=True, hide_index=True)
        else:
            # Render card-based layout
            for index, row in display_df.iterrows():
                # Outer glass card container using native st.container with border
                with st.container(border=True):
                    # Define layout
                    col_details, col_actions = st.columns([3, 1])
                    
                    with col_details:
                        name_display = row["Customer Name"] if row["Customer Name"] else "*(No Name Entered)*"
                        # License plate styling for Vehicle Number
                        v_num_plate = f'<span class="license-plate">{row["Vehicle Number"]}</span>'
                        
                        st.markdown(f"#### 👤 {name_display}")
                        st.markdown(
                            f"{v_num_plate} &nbsp;&nbsp; **Model:** `{row['Vehicle Model']}` &nbsp;&nbsp;|&nbsp;&nbsp; **Color:** `{row['Vehicle Color']}`", 
                            unsafe_allow_html=True
                        )
                        
                        # Service history and amount
                        bill_numbers = row["Bill Number(s)"] if row["Bill Number(s)"] else "None"
                        st.markdown(
                            f"💰 **Total Paid:** `₹{row['Total Amount']:,.2f}` &nbsp;&nbsp;|&nbsp;&nbsp; 🧾 **Bills:** `{bill_numbers}`"
                        )
                        
                        # Service coating dates
                        free_buff_date = row["Free Buffing Date"] if row["Free Buffing Date"] else "*(Blank)*"
                        st.markdown(
                            f"📅 **Coating Date:** `{row['Coating Date']}` &nbsp;&nbsp;|&nbsp;&nbsp; 🔁 **Free Buffing Date:** `{free_buff_date}`"
                        )
                    
                    with col_actions:
                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                        if st.button("✏️ Edit Profile", key=f"edit_prof_{row['ID']}", use_container_width=True, type="primary"):
                            st.session_state.edit_customer_id = int(row['ID'])
                            st.session_state.log_visit_customer_id = None
                            st.rerun()
                            
                        if st.button("🔁 Log Return", key=f"log_visit_btn_{row['ID']}", use_container_width=True):
                            st.session_state.log_visit_customer_id = int(row['ID'])
                            st.session_state.edit_customer_id = None
                            st.rerun()
        
        # Download buttons
        st.markdown("### 📥 Download & Export")
        csv = filtered_df[cols_to_show].to_csv(index=False).encode('utf-8')
        
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                label="📁 Export to CSV",
                data=csv,
                file_name=f"coating_records_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with dl_col2:
            # Create a simplified text representation of customer list
            text_lines = []
            for _, row in filtered_df.iterrows():
                cust_name = row['Customer Name'] if row['Customer Name'] else "N/A"
                free_buff_date = row['Free Buffing Date'] if row['Free Buffing Date'] else "N/A"
                text_lines.append(
                    f"Name: {cust_name} | "
                    f"Vehicle: {row['Vehicle Number']} ({row['Vehicle Model']}) | "
                    f"Bills: {row['Bill Number(s)']} | "
                    f"Coating Date: {row['Coating Date']} | "
                    f"Free Buffing Date: {free_buff_date} | "
                    f"Total Paid: ₹{row['Total Amount']}"
                )
            customer_text = "\n".join(text_lines).encode('utf-8')
            
            st.download_button(
                label="📄 Download Customer List (TXT)",
                data=customer_text,
                file_name=f"customer_list_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )

# ================= TAB 2: ADD CUSTOMER =================
with tab2:
    st.subheader("➕ Add New Customer & Vehicle Details")
    
    with st.form("add_customer_form", clear_on_submit=True):
        name = st.text_input("Customer Name (Optional)", placeholder="Enter customer's name")
        v_num = st.text_input("Vehicle Number*", placeholder="e.g. MH12AB1234").upper().strip()
        v_model = st.selectbox(
            "Vehicle Model*",
            options=all_models,
            index=None,
            placeholder="Select or type model...",
            accept_new_options=True,
            key="add_cust_v_model"
        )

        v_color = st.selectbox(
            "Vehicle Color*",
            options=all_colors,
            index=None,
            placeholder="Select or type color...",
            accept_new_options=True,
            key="add_cust_v_color"
        )
        
        # Payment details
        st.markdown("### 💳 Initial Payment Details")
        bill_number = st.text_input("Bill Number (Optional)", placeholder="e.g. B-101")
        payment_amount = st.number_input("Payment Amount (₹)*", min_value=0.0, value=0.0, step=50.0)
        
        # Coating date
        coating_date = st.date_input("Coating Date*", value=datetime.today())
        
        st.markdown("*Required fields")
        
        submit_btn = st.form_submit_button("Submit Record", use_container_width=True)
        
        if submit_btn:
            v_model_str = v_model.strip().upper() if v_model else ""
            v_color_str = v_color.strip().upper() if v_color else ""
            
            # Validations
            if not v_num.strip():
                st.error("Vehicle Number is required.")
            elif not v_model_str:
                st.error("Vehicle Model is required.")
            elif not v_color_str:
                st.error("Vehicle Color is required.")
            else:
                formatted_date = coating_date.strftime("%Y-%m-%d")
                cust_name_val = name.strip() if name.strip() else None
                bill_no_val = bill_number.strip() if bill_number.strip() else None
                status_val = "Paid" if payment_amount > 0.0 else "Pending"
                success, msg = db.add_customer(
                    cust_name_val, 
                    v_num, 
                    v_model_str, 
                    v_color_str, 
                    formatted_date,
                    payment_amount,
                    status_val,
                    bill_no_val
                )
                if success:
                    st.success(f"Successfully added record for vehicle {v_num}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"Error adding record: {msg}")

# ================= TAB 3: LOG RETURN VISIT =================
with tab3:
    st.subheader("🔁 Log Return Coating Visit")
    
    if df_records.empty:
        st.info("No customers available. Please add a customer profile first.")
    else:
        # User selects existing customer
        customer_options = df_records.to_dict('records')
        
        def format_cust_label(row):
            cust_name = row['Customer Name'] if row['Customer Name'] else "N/A"
            return f"{cust_name} - {row['Vehicle Number']} ({row['Vehicle Model']})"
            
        selected_cust = st.selectbox(
            "Select Returning Customer/Vehicle*",
            options=customer_options,
            format_func=format_cust_label
        )
        
        if selected_cust:
            cust_id = selected_cust["ID"]
            
            with st.form("return_visit_form", clear_on_submit=True):
                cust_name_lbl = selected_cust['Customer Name'] if selected_cust['Customer Name'] else "N/A"
                st.markdown(f"**Logging return visit for:** `{cust_name_lbl}` (Vehicle: `{selected_cust['Vehicle Number']}`)")
                
                # Input visit details
                return_bill = st.text_input("Bill Number (Optional)", placeholder="e.g. B-102")
                return_date = st.date_input("Coating Date*", value=datetime.today())
                return_amount = st.number_input("Payment Amount (₹)*", min_value=0.0, value=0.0, step=50.0)
                st.markdown("*Required fields")
                visit_submit = st.form_submit_button("Log Return Visit", use_container_width=True)
                
                if visit_submit:
                    formatted_return_date = return_date.strftime("%Y-%m-%d")
                    bill_no_val = return_bill.strip() if return_bill.strip() else None
                    status_val = "Paid" if return_amount > 0.0 else "Pending"
                    success, msg = db.add_visit(
                        cust_id,
                        formatted_return_date,
                        return_amount,
                        status_val,
                        bill_no_val
                    )
                    if success:
                        st.success(f"Coating visit successfully logged on {formatted_return_date}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"Error logging visit: {msg}")

# ================= TAB 4: MANAGE RECORDS =================
with tab4:
    st.subheader("⚙️ Edit Customer Profile & Coating Visits")
    
    if df_records.empty:
        st.info("No records available to edit or delete.")
    else:
        # Select customer
        options = df_records.to_dict('records')
        
        def get_label(row):
            cust_name = row['Customer Name'] if row['Customer Name'] else "N/A"
            return f"{cust_name} - {row['Vehicle Number']}"
            
        selected_record = st.selectbox(
            "Select Customer to Modify/Delete",
            options=options,
            format_func=get_label,
            key="manage_cust_selectbox"
        )
        
        if selected_record:
            cust_id = selected_record["ID"]
            
            # --- SECTION 1: EDIT CUSTOMER PROFILE ---
            st.markdown("### 👤 Edit Customer Profile")
            with st.expander("Show Profile Fields", expanded=False):
                edit_name = st.text_input("Edit Customer Name (Optional)", value=selected_record["Customer Name"] if selected_record["Customer Name"] else "")
                             # Model selection logic
                curr_model = selected_record["Vehicle Model"].upper().strip() if selected_record["Vehicle Model"] else ""
                options_models = all_models.copy()
                if curr_model and curr_model not in options_models:
                    options_models.append(curr_model)
                
                edit_v_model = st.selectbox(
                    "Edit Vehicle Model",
                    options=options_models,
                    index=options_models.index(curr_model) if curr_model in options_models else None,
                    placeholder="Select or type model...",
                    accept_new_options=True,
                    key="edit_v_model_sel_tab4"
                )

                # Color selection logic
                curr_color = selected_record["Vehicle Color"].upper().strip() if selected_record["Vehicle Color"] else ""
                options_colors = all_colors.copy()
                if curr_color and curr_color not in options_colors:
                    options_colors.append(curr_color)
                
                edit_v_color = st.selectbox(
                    "Edit Vehicle Color",
                    options=options_colors,
                    index=options_colors.index(curr_color) if curr_color in options_colors else None,
                    placeholder="Select or type color...",
                    accept_new_options=True,
                    key="edit_v_color_sel_tab4"
                )
                
                profile_col1, profile_col2 = st.columns(2)
                with profile_col1:
                    update_profile = st.button("💾 Save Profile Changes", use_container_width=True, type="primary")
                    if update_profile:
                        edit_v_model_str = edit_v_model.strip().upper() if edit_v_model else ""
                        edit_v_color_str = edit_v_color.strip().upper() if edit_v_color else ""
                        
                        if not edit_v_num.strip():
                            st.error("Vehicle Number cannot be empty.")
                        elif not edit_v_model_str:
                            st.error("Vehicle Model cannot be empty.")
                        elif not edit_v_color_str:
                            st.error("Vehicle Color cannot be empty.")
                        else:
                            cust_name_val = edit_name.strip() if edit_name.strip() else None
                            success, msg = db.update_customer(
                                cust_id,
                                cust_name_val,
                                edit_v_num,
                                edit_v_model_str,
                                edit_v_color_str
                            )
                            if success:
                                st.success("Customer profile updated successfully!")
                                st.rerun()
                            else:
                                st.error(f"Error updating profile: {msg}")
                                
                with profile_col2:
                    cust_name_del = selected_record['Customer Name'] if selected_record['Customer Name'] else "this vehicle"
                    with st.popover("🗑️ Delete Full Customer Profile", use_container_width=True):
                        st.warning(f"Warning: This will delete {cust_name_del} and ALL coating history records. Are you sure?")
                        confirm_delete = st.button("Yes, Delete Profile & History", use_container_width=True)
                        if confirm_delete:
                            success, msg = db.delete_customer(cust_id)
                            if success:
                                st.success("Customer profile deleted successfully!")
                                st.rerun()
                            else:
                                st.error(f"Error deleting customer: {msg}")
            
            st.markdown("---")
            
            # --- SECTION 2: MANAGE COATING VISITS ---
            st.markdown("### 🔧 Manage Coating Visits (Dates & Payments)")
            visits = db.get_customer_visits(cust_id)
            
            if not visits:
                st.info("No coating history visits logged for this customer.")
            else:
                # View visits table
                visits_df = pd.DataFrame(visits)
                visits_df = visits_df.rename(columns={
                    "id": "Visit ID",
                    "coating_date": "Coating Date",
                    "payment_amount": "Amount (₹)",
                    "payment_status": "Status",
                    "bill_number": "Bill Number"
                })
                # Replace None with empty string for display
                visits_df["Bill Number"] = visits_df["Bill Number"].fillna("")
                st.dataframe(visits_df[["Visit ID", "Coating Date", "Bill Number", "Amount (₹)", "Status"]], use_container_width=True, hide_index=True)
                
                # Edit individual visits
                st.markdown("#### Edit / Delete Specific Visit")
                visit_options = visits_df.to_dict('records')
                
                def get_visit_label(visit_row):
                    bill_no = visit_row['Bill Number'] if visit_row['Bill Number'] else "N/A"
                    return f"Visit ID {visit_row['Visit ID']} - Date: {visit_row['Coating Date']} (Bill: {bill_no} | ₹{visit_row['Amount (₹)']} - {visit_row['Status']})"
                    
                selected_visit = st.selectbox(
                    "Select Visit to Modify",
                    options=visit_options,
                    format_func=get_visit_label
                )
                
                if selected_visit:
                    v_id = selected_visit["Visit ID"]
                    
                    # Pre-parse date
                    try:
                        v_date = datetime.strptime(selected_visit["Coating Date"], "%Y-%m-%d").date()
                    except Exception:
                        v_date = datetime.today().date()
                        
                    edit_v_bill = st.text_input("Edit Bill Number", value=selected_visit["Bill Number"] if selected_visit["Bill Number"] else "", key=f"edit_v_bill_{v_id}")
                    edit_v_date = st.date_input("Edit Coating Date", value=v_date, key=f"edit_v_date_{v_id}")
                    edit_v_amount = st.number_input("Edit Visit Amount (₹)", min_value=0.0, value=float(selected_visit["Amount (₹)"]), step=50.0, key=f"edit_v_amount_{v_id}")
                    
                    v_btn_col1, v_btn_col2 = st.columns(2)
                    with v_btn_col1:
                        save_visit = st.button("💾 Save Visit Details", use_container_width=True, key=f"save_v_btn_{v_id}")
                        if save_visit:
                            formatted_v_date = edit_v_date.strftime("%Y-%m-%d")
                            bill_no_val = edit_v_bill.strip() if edit_v_bill.strip() else None
                            status_val = "Paid" if edit_v_amount > 0.0 else "Pending"
                            success, msg = db.update_visit(v_id, formatted_v_date, edit_v_amount, status_val, bill_no_val)
                            if success:
                                st.success("Coating visit updated successfully!")
                                st.rerun()
                            else:
                                st.error(f"Error updating visit: {msg}")
                                
                    with v_btn_col2:
                        with st.popover("🗑️ Delete This Visit Only", use_container_width=True):
                            st.warning("Are you sure you want to delete this specific visit record?")
                            confirm_v_delete = st.button("Yes, Delete Visit", use_container_width=True, key=f"del_v_btn_{v_id}")
                            if confirm_v_delete:
                                success, msg = db.delete_visit(v_id)
                                if success:
                                    st.success("Visit deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Error deleting visit: {msg}")
