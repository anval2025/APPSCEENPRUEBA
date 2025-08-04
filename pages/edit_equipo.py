import streamlit as st
import sqlite3

DB = "data/plantlist.db"

def editar_equipo():
    st.subheader("Editar equipo existente")

    nombre_equipo = st.text_input("Buscar por nombre del equipo", key="buscar_equipo")

    if st.button("Buscar"):
        if not nombre_equipo.strip():
            st.warning("Por favor escribe el nombre del equipo")
        else:
            # Abrimos conexión y cursor
            conn = sqlite3.connect(DB)
            c = conn.cursor()

            # Obtenemos la estructura de la tabla antes de cerrar conexión
            campos = [col[1] for col in c.execute("PRAGMA table_info(equipos)")]

            # Ejecutamos consulta para obtener equipos que coincidan (búsqueda parcial, case insensitive)
            c.execute("SELECT * FROM equipos WHERE LOWER(equipo) LIKE ?", (f"%{nombre_equipo.lower()}%",))
            equipos = c.fetchall()

            # Cerramos conexión
            conn.close()

            if equipos:
                st.session_state['equipos_encontrados'] = equipos
                st.session_state['campos'] = campos
                st.success(f"Se encontraron {len(equipos)} equipo(s)")
            else:
                st.warning("No se encontraron equipos con ese nombre")
                st.session_state['equipos_encontrados'] = []
                st.session_state['campos'] = []

    # Mostrar resultados si existen
    if 'equipos_encontrados' in st.session_state and st.session_state['equipos_encontrados']:
        campos = st.session_state['campos']
        for idx, equipo in enumerate(st.session_state['equipos_encontrados']):
            data = dict(zip(campos, equipo))

            with st.form(f"form_editar_{idx}"):
                st.write(f"### Editar equipo: {data['equipo']} (Serie: {data['num_serie']})")
                data["tipo_equipo"] = st.text_input("Tipo de equipo", value=data["tipo_equipo"])
                data["equipo"] = st.text_input("Nombre del equipo", value=data["equipo"])
                data["capacidad"] = st.text_input("Capacidad (SWL)", value=data["capacidad"])
                status_anterior = data["status"]
                data["status"] = st.selectbox(
                    "Status",
                    ["DISPONIBLE", "NO DISPONIBLE", "NO DISPONIBLE ALTA INVERSION"],
                    index=["DISPONIBLE", "NO DISPONIBLE", "NO DISPONIBLE ALTA INVERSION"].index(data["status"])
                )
                data["fabricante"] = st.text_input("Fabricante", value=data["fabricante"])
                data["fabricacion"] = st.text_input("Año de fabricación", value=data["fabricacion"])
                data["modelo"] = st.text_input("Modelo", value=data["modelo"])
                data["fabricante_engine"] = st.text_input("Fabricante del motor", value=data["fabricante_engine"])
                data["fabricante_transmision"] = st.text_input("Fabricante de transmisión", value=data["fabricante_transmision"])
                data["puesta_marcha"] = st.text_input("Fecha de puesta en marcha", value=data["puesta_marcha"])
                data["leased_own"] = st.text_input("Propiedad (Leased/Own)", value=data["leased_own"])
                data["location"] = st.text_input("Ubicación", value=data["location"])
                data["observaciones"] = st.text_area("Observaciones", value=data["observaciones"])

                guardar = st.form_submit_button("Guardar cambios")

                if guardar:
                    conn = sqlite3.connect(DB)
                    c = conn.cursor()
                    c.execute("""
                        UPDATE equipos SET 
                            tipo_equipo=?, equipo=?, capacidad=?, status=?, fabricante=?, 
                            fabricacion=?, modelo=?, fabricante_engine=?, fabricante_transmision=?, 
                            puesta_marcha=?, leased_own=?, location=?, observaciones=?
                        WHERE num_serie=?
                    """, (
                        data["tipo_equipo"], data["equipo"], data["capacidad"], data["status"], data["fabricante"],
                        data["fabricacion"], data["modelo"], data["fabricante_engine"], data["fabricante_transmision"],
                        data["puesta_marcha"], data["leased_own"], data["location"], data["observaciones"], data["num_serie"]
                    ))

                    if status_anterior != data["status"]:
                        c.execute("""
                            INSERT INTO historial_status (num_serie, status_anterior, status_nuevo, usuario)
                            VALUES (?, ?, ?, ?)
                        """, (
                            data["num_serie"], status_anterior, data["status"], st.session_state.get("usuario", "admin")
                        ))

                    conn.commit()
                    conn.close()
                    st.success("Datos actualizados correctamente")
