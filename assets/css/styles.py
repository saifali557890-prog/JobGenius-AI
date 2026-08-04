import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        /* ===== Blue-Teal Mesh Background ===== */
        .stApp {
            background-color: #050B14;
            background-image: 
                radial-gradient(at 15% 10%, rgba(14, 165, 233, 0.22) 0px, transparent 55%),
                radial-gradient(at 85% 0%, rgba(20, 184, 166, 0.18) 0px, transparent 50%),
                radial-gradient(at 50% 100%, rgba(2, 132, 199, 0.16) 0px, transparent 55%);
            background-attachment: fixed;
        }

        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 2rem !important;
            max-width: 95% !important;
        }

        /* ===== Titles ===== */
        h1 {
            font-weight: 800 !important;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #38BDF8 0%, #2DD4BF 50%, #0EA5E9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 10px 30px rgba(56, 189, 248, 0.25);
            margin-bottom: 0.5rem !important;
        }

        h2, h3 {
            color: #F8FAFC !important;
            font-weight: 700 !important;
        }

        /* ===== Glass Cards ===== */
        .glass-card {
            background: rgba(15, 23, 42, 0.65) !important;
            backdrop-filter: blur(16px) saturate(180%);
            -webkit-backdrop-filter: blur(16px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 20px !important;
            padding: 28px !important;
            margin-bottom: 24px !important;
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
        }

        /* ===== Metric Cards ===== */
        .metric-card {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.5) 100%);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 16px;
            padding: 22px 18px;
            text-align: center;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            color: #38BDF8;
        }

        .metric-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: #94A3B8;
        }

        /* ===== Custom Sidebar ===== */
        section[data-testid="stSidebar"] {
            background-color: #0B0F19 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }

        /* ===== Custom Buttons ===== */
        .stButton > button {
            background: linear-gradient(135deg, #0EA5E9 0%, #2DD4BF 100%) !important;
            color: #000000 !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 10px 24px !important;
        }
    </style>
    """, unsafe_allow_html=True)