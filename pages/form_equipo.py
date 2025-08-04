import streamlit as st
import sqlite3
from datetime import date

DB = "data/plantlist.db"

def agregar_equipo():
    st.subheader("Agregar nuevo equipo")
    with st.form("form_agregar"):
        tipo_equipo = st.text_input("Tipo de equipo")
        equipo = st.text_input("Nombre del equipo")
        capacidad = st.text_input("Capacidad (SWL)")
        status = st.selectbox("Status", ["DISPONIBLE", "NO DISPONIBLE", "NO DISPONIBLE ALTA INVERSION"])
        num_serie = st.text_input("Número de serie")
        fabricante = st.text_input("Fabricante")
        fabricacion = st.text_input("Año de fabricación")
        modelo = st.text_input("Modelo")
        fabricante_engine = st.text_input("Fabricante del motor")
        fabricante_transmision = st.text_input("Fabricante de transmisión")
        puesta_marcha = st.date_input("Puesta en marcha", value=date.today())
        leased_own = st.text_input("Leased/Own")
        location = st.text_input("Ubicación")
        observaciones = st.text_area("Observaciones")
        submit = st.form_submit_button("Guardar equipo")

        if submit:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            try:
                c.execute('''
                    INSERT INTO equipos (tipo_equipo, equipo, capacidad, status, num_serie, fabricante, fabricacion,
                        modelo, fabricante_engine, fabricante_transmision, puesta_marcha, leased_own, location, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (tipo_equipo, equipo, capacidad, status, num_serie, fabricante, fabricacion,
                      modelo, fabricante_engine, fabricante_transmision, puesta_marcha, leased_own, location, observaciones))
                conn.commit()
                st.success("Equipo agregado correctamente.")
            except sqlite3.IntegrityError:
                st.error("Ya existe un equipo con ese número de serie.")
            conn.close()
