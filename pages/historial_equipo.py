import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO

DB = "data/plantlist.db"

def historial_equipo():
    st.subheader("Historial de cambios de status")
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        SELECT e.tipo_equipo, e.equipo, e.num_serie, e.fabricante, e.leased_own, e.location, e.observaciones,
               h.status_anterior, h.status_nuevo, h.fecha_cambio, h.usuario
        FROM historial_status h
        LEFT JOIN equipos e ON h.num_serie = e.num_serie
        ORDER BY h.fecha_cambio DESC
    """)
    rows = c.fetchall()

    if not rows:
        st.info("No hay historial registrado.")
        conn.close()
        return

    columnas = [
        "Tipo de Equipo", "Equipo", "Número de Serie", "Fabricante", "Propiedad (Leased/Own)",
        "Ubicación", "Observaciones", "Status Anterior", "Status Nuevo", "Fecha de Cambio", "Usuario"
    ]
    df = pd.DataFrame(rows, columns=columnas)
    st.dataframe(df)

    # Descargar Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Historial")
    data = output.getvalue()

    st.download_button(
        "Descargar historial en Excel",
        data=data,
        file_name="historial_equipos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    conn.close()
