import streamlit as st
from audit_ui import run_audit_ui

if __name__ == "__main__":
    st.set_page_config(page_title="Green IT Calculator", page_icon="🌿", layout="wide")
    run_audit_ui()