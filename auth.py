import hashlib
import streamlit as st
import database

# Use a fixed salt for simplicity and consistency across the app
SALT = "workshop_secure_salt_2026"

def hash_password(password):
    """Hashes a password with a predefined salt using SHA-256."""
    salted = password + SALT
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def verify_login(username, password):
    """Verifies user credentials against the SQLite database."""
    user = database.get_user_by_username(username)
    if not user:
        return False, None
    
    hashed = hash_password(password)
    if user['password_hash'] == hashed:
        return True, user['role']
    return False, None

def login_user(username, role):
    """Sets session state variables to log the user in."""
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.user_role = role
    st.rerun()

def logout_user():
    """Clears login state and logs the user out."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.rerun()

def show_login_page():
    """Displays a modern login interface styled for Vehicle Customer Hub."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        /* Font style */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        .login-container {
            max-width: 420px;
            margin: 4% auto;
            padding: 24px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            color: #f8fafc;
            text-align: center;
        }
        .login-title {
            font-size: 26px;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }
        .login-subtitle {
            font-size: 13px;
            color: #94a3b8;
            margin-bottom: 10px;
            font-weight: 400;
        }
        
        /* Form inputs styling */
        div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 8px !important;
        }
        
        /* Forms container */
        .stForm {
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            background-color: rgba(255, 255, 255, 0.01) !important;
        }
        
        /* Buttons styling */
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

        /* Tabs styling */
        div[data-testid="stTabBar"] {
            background-color: rgba(255, 255, 255, 0.01) !important;
            border-radius: 12px !important;
            padding: 4px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            margin-bottom: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="login-container">
            <div class="login-title">✨ MAHAVEER AUTO SHINER</div>
            <div class="login-subtitle">Simple & Mobile-Friendly Coating Records</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Outer columns to center the login form card
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Register New Account"])
        
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                username_input = st.text_input("Username", placeholder="e.g. admin").strip().lower()
                password_input = st.text_input("Password", type="password", placeholder="••••••••")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    if not username_input or not password_input:
                        st.error("Please enter both username and password.")
                    else:
                        success, role = verify_login(username_input, password_input)
                        if success:
                            st.success(f"Welcome back, {username_input}!")
                            login_user(username_input, role)
                        else:
                            st.error("Invalid username or password.")
                            
        with tab_register:
            with st.form("register_form", clear_on_submit=True):
                reg_username = st.text_input("Desired Username *", placeholder="e.g. john_doe").strip().lower()
                reg_password = st.text_input("Choose Password *", type="password", placeholder="••••••••")
                reg_confirm = st.text_input("Confirm Password *", type="password", placeholder="••••••••")
                reg_role = st.selectbox("Role Permission", ["Staff", "Admin"])
                
                submit_reg = st.form_submit_button("Register & Create Account", use_container_width=True)
                
                if submit_reg:
                    if not reg_username or not reg_password:
                        st.error("Username and password are required.")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match.")
                    elif len(reg_password) < 4:
                        st.error("Password must be at least 4 characters long.")
                    else:
                        hpw = hash_password(reg_password)
                        success = database.add_user(reg_username, hpw, reg_role)
                        if success:
                            st.success(f"Account '{reg_username}' registered successfully! You can now sign in using the 'Sign In' tab.")
                        else:
                            st.error("Username already exists. Please choose another one.")
                            
        # Helpful credentials tooltip for testing
        st.info("💡 **Default Credentials:**\n- Admin: `admin` / `admin123`\n- Staff: `staff` / `staff123`")
        
        # Helpful credentials tooltip for testing
        st.info("💡 **Default Credentials:**\n- Admin: `admin` / `admin123`\n- Staff: `staff` / `staff123`")
