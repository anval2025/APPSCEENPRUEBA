import streamlit as st

def login_page():
    st.markdown("<h1 style='text-align: center;'>CONTROL DE EQUIPO</h1>", unsafe_allow_html=True)
    st.write("")
    with st.form("login_form"):
        username = st.text_input("Usuario", placeholder="Ingrese su usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar")

        if submitted:
            if username == "admin" and password == "admin":
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'admin'
            elif username == "invitado" and password == "invitado":
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'invitado'
            else:
                st.error("Usuario o contraseña incorrectos")
