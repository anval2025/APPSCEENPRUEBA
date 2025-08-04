import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta
from contextlib import contextmanager

from pages.form_equipo import agregar_equipo
from pages.edit_equipo import editar_equipo
from pages.historial_equipo import historial_equipo

DB = "data/plantlist.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB)
    try:
        yield conn
    finally:
        conn.close()

def admin_dashboard():
    st.title("Panel Administrador")

    if 'admin_panel' not in st.session_state:
        st.session_state['admin_panel'] = None

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        if st.button("➕ Agregar equipo"):
            st.session_state['admin_panel'] = 'agregar'

    with col2:
        if st.button("✏️ Editar Equipo"):
            st.session_state['admin_panel'] = 'editar'

    with col3:
        if st.button("🕒 Reporte Historia"):
            st.session_state['admin_panel'] = 'historial'

    with col4:
        if st.button("📈 Reporte Plantlist"):
            st.session_state['admin_panel'] = 'todos'

    with col5:
        if st.button("⛽ Recarga Diesel"):
            st.session_state['admin_panel'] = 'recarga_diesel'

    with col6:
        if st.button("📈 Reporte Recarga"):
            st.session_state['admin_panel'] = 'reporte_recargas'

    with col7:
        if st.button("⏳ Diesel Pendientes"):
            st.session_state['admin_panel'] = 'recargas_pendientes'

    st.markdown("---")

    panel = st.session_state['admin_panel']

    if panel == 'agregar':
        agregar_equipo()
    elif panel == 'editar':
        editar_equipo()
    elif panel == 'historial':
        historial_equipo()
    elif panel == 'todos':
        mostrar_todos_equipos()
    elif panel == 'recarga_diesel':
        mostrar_botones_recarga()
    elif panel == 'reporte_recargas':
        reporte_recargas()
    elif panel == 'recargas_pendientes':
        recargas_diesel_pendientes()

def mostrar_todos_equipos():
    with get_db_connection() as conn:
        df_original = pd.read_sql_query("SELECT * FROM equipos", conn)

    st.subheader("Tabla completa de equipos con buscador general")

    if 'busqueda_general' not in st.session_state:
        st.session_state['busqueda_general'] = ""

    with st.expander("🔍 Buscar en toda la tabla", expanded=True):
        st.session_state['busqueda_general'] = st.text_input(
            "Escribe texto a buscar en cualquier columna:",
            value=st.session_state['busqueda_general']
        )

        if st.button("❌ Limpiar búsqueda"):
            st.session_state['busqueda_general'] = ""
            # No se usa experimental_rerun()

    df_filtrado = df_original.copy()
    texto = st.session_state['busqueda_general'].strip().lower()

    if texto:
        df_filtrado = df_filtrado[df_filtrado.apply(
            lambda row: row.astype(str).str.lower().str.contains(texto).any(),
            axis=1
        )]

        def resaltar_celda(val):
            if texto in str(val).lower():
                return 'background-color: #ffff99; font-weight: bold; color: red;'
            return ''

        styled_df = df_filtrado.style.applymap(resaltar_celda)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.dataframe(df_filtrado, use_container_width=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name="Equipos_Completos")
    data = output.getvalue()

    st.download_button(
        label="⬇️ Descargar Excel filtrado",
        data=data,
        file_name="equipos_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def mostrar_botones_recarga():
    st.subheader("Selecciona tipo de equipo para registrar recarga")

    tipos_equipo = [
        ("Tractoplana", "Tractoplana"),
        ("Grúa Marco", "Marco"),
        ("Grúa Marco Eléctrica", "MarcoElectrica"),
        ("Grúa Llenos", "Llenos"),
        ("Grúa Vacíos", "Vacios")
    ]

    cols = st.columns(len(tipos_equipo))
    for col, (label, tipo) in zip(cols, tipos_equipo):
        with col:
            if st.button(label):
                st.session_state['recarga_tipo'] = tipo

    if 'recarga_tipo' in st.session_state:
        mostrar_formulario_recarga(st.session_state['recarga_tipo'])

def mostrar_formulario_recarga(tipo_equipo):
    st.subheader(f"Formulario de Recarga: {tipo_equipo}")

    condiciones = {
        "Tractoplana": "LOWER(tipo_equipo) LIKE '%tracto%' AND location = 'LCT' AND equipo NOT LIKE '%OTTA%' AND equipo NOT LIKE '%EHT%'",
        "Marco": "tipo_equipo = 'GRUA DE MARCO'",
        "MarcoElectrica": "tipo_equipo = 'GRUA DE MARCO ELECTRICA'",
        "Llenos": "tipo_equipo = 'GRUA MOVIL MANIPULADOR PARA LLENOS'",
        "Vacios": "tipo_equipo = 'GRUA MOVIL MANIPULADOR PARA VACIOS'"
    }

    tabla = {
        "Tractoplana": "DieselTractoplanas",
        "Marco": "DieselMarco",
        "MarcoElectrica": "DieselMarco",
        "Llenos": "DieselLlenos",
        "Vacios": "DieselVacios"
    }

    with get_db_connection() as conn:
        df = pd.read_sql_query(f"SELECT equipo FROM equipos WHERE {condiciones[tipo_equipo]}", conn)
        equipos = df['equipo'].tolist()

        if not equipos:
            st.warning("No hay equipos registrados.")
            return

    equipo = st.selectbox("Selecciona un equipo", equipos)
    cantidad = st.number_input("Cantidad de diesel (litros)", min_value=1, step=1)
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    col1, col2 = st.columns(2)

    with get_db_connection() as conn:
        with col1:
            if st.button("Guardar Recarga"):
                conn.execute(f"""
                    INSERT INTO {tabla[tipo_equipo]} (equipo, fecha_hora, cantidad)
                    VALUES (?, ?, ?)
                """, (equipo, fecha_hora, cantidad))
                conn.commit()
                st.success("Recarga registrada correctamente.")
                st.session_state.pop('recarga_tipo', None)
                # No experimental_rerun()

        with col2:
            if st.button("Cancelar"):
                st.session_state.pop('recarga_tipo', None)
                # No experimental_rerun()

def reporte_recargas():
    st.subheader("Reporte de Recargas por Periodo")

    fecha_inicio = st.date_input("Fecha inicio", datetime.now().date() - timedelta(days=7))
    fecha_fin = st.date_input("Fecha fin", datetime.now().date())

    if fecha_inicio > fecha_fin:
        st.warning("La fecha de inicio no puede ser mayor que la fecha final.")
        return

    if st.button("Generar Reporte"):
        fecha_inicio_str = f"{fecha_inicio} 00:00:00"
        fecha_fin_str = f"{fecha_fin} 23:59:59"

        dfs = []
        tablas = {
            "DieselTractoplanas": "Tractoplana",
            "DieselMarco": "Marco",
            "DieselLlenos": "Llenos",
            "DieselVacios": "Vacios"
        }

        with get_db_connection() as conn:
            for tabla, tipo in tablas.items():
                df = pd.read_sql_query(f"""
                    SELECT '{tipo}' AS tipo_equipo, equipo, fecha_hora, cantidad
                    FROM {tabla}
                    WHERE fecha_hora BETWEEN ? AND ?
                """, conn, params=(fecha_inicio_str, fecha_fin_str))
                dfs.append(df)

        if dfs:
            df_final = pd.concat(dfs, ignore_index=True)
            st.dataframe(df_final)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False, sheet_name="Recargas")
            data = output.getvalue()

            st.download_button(
                label="Descargar Excel de Recargas",
                data=data,
                file_name=f"recargas_{fecha_inicio}_a_{fecha_fin}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No hay recargas en este periodo.")

def recargas_diesel_pendientes():
    st.subheader("Recargas Diesel Pendientes en últimas 24 horas (Ubicación: LCT)")

    ahora = datetime.now()
    hace_24h = ahora - timedelta(hours=24)
    fecha_limite = hace_24h.strftime('%Y-%m-%d %H:%M:%S')

    categorias = {
        "Tractoplana": {
            "tabla": "DieselTractoplanas",
            "condicion": "LOWER(tipo_equipo) LIKE '%tracto%' AND location = 'LCT' AND equipo NOT LIKE '%OTTA%' AND equipo NOT LIKE '%EHT%'"
        },
        "Grúas de Marco": {
            "tabla": "DieselMarco",
            "condicion": "(tipo_equipo = 'GRUA DE MARCO' OR tipo_equipo = 'GRUA DE MARCO ELECTRICA') AND location = 'LCT'"
        },
        "Llenos": {
            "tabla": "DieselLlenos",
            "condicion": "tipo_equipo = 'GRUA MOVIL MANIPULADOR PARA LLENOS' AND location = 'LCT'"
        },
        "Vacíos": {
            "tabla": "DieselVacios",
            "condicion": "tipo_equipo = 'GRUA MOVIL MANIPULADOR PARA VACIOS' AND location = 'LCT'"
        }
    }

    resumen = []
    detalle = []

    with get_db_connection() as conn:
        for categoria, info in categorias.items():
            df_equipos = pd.read_sql_query(f"SELECT equipo FROM equipos WHERE {info['condicion']}", conn)
            equipos = df_equipos['equipo'].tolist()

            if not equipos:
                continue

            df_recargados = pd.read_sql_query(f"""
                SELECT DISTINCT equipo FROM {info['tabla']}
                WHERE fecha_hora >= ?
            """, conn, params=(fecha_limite,))
            recargados = set(df_recargados['equipo'].tolist())

            df_ultimas = pd.read_sql_query(f"""
                SELECT equipo, MAX(fecha_hora) AS ultima_recarga
                FROM {info['tabla']}
                GROUP BY equipo
            """, conn)

            pendientes = [eq for eq in equipos if eq not in recargados]

            resumen.append({
                "Categoría": categoria,
                "Equipos Pendientes": len(pendientes)
            })

            for eq in pendientes:
                ultima_recarga = df_ultimas.loc[df_ultimas['equipo'] == eq, 'ultima_recarga']
                detalle.append({
                    "Categoría": categoria,
                    "Equipo": eq,
                    "Última Recarga": ultima_recarga.values[0] if not ultima_recarga.empty else "Sin registro"
                })

    df_resumen = pd.DataFrame(resumen)
    st.table(df_resumen)

    if detalle:
        st.markdown("### Equipos Pendientes Detallados")
        df_detalle = pd.DataFrame(detalle)
        st.dataframe(
            df_detalle.style.set_properties(**{
                'font-size': '12px',
                'padding': '2px'
            }),
            use_container_width=True
        )
    else:
        st.success("No hay equipos pendientes de recarga en las últimas 24 horas.")
