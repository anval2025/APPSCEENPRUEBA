import streamlit as st
from pages.login import login_page
from utils.session import init_session_state

st.set_page_config(page_title="CONTROL DE EQUIPO", layout="wide")
init_session_state()

# Leer parámetros de la URL
params = st.query_params
modo_admin = params.get("modo_admin", "false").lower() == "true"

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    login_page()
else:
    if st.session_state['role'] == 'admin':
        # Botón para cambiar entre modo invitado y modo administrador
        col1, col2 = st.columns([1, 9])
        with col1:
            if modo_admin:
                if st.button("Ver Panel Invitado"):
                    st.query_params["modo_admin"] = "false"
                    st.rerun()
            else:
                if st.button("Panel administrativo"):
                    st.query_params["modo_admin"] = "true"
                    st.rerun()
        with col2:
            st.markdown("### Panel Administrador" if modo_admin else "### Panel Invitado")

        # Mostrar el panel correspondiente
        if modo_admin:
            from pages.admin import admin_dashboard
            admin_dashboard()
        else:
            from pages.invitado import invitado_dashboard
            invitado_dashboard()
    else:
        from pages.invitado import invitado_dashboard
        invitado_dashboard()
