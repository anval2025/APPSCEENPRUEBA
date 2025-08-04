import sqlite3

conn = sqlite3.connect("data/plantlist.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS equipos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_equipo TEXT,
    equipo TEXT,
    capacidad TEXT,
    status TEXT CHECK(status IN ('DISPONIBLE', 'NO DISPONIBLE', 'NO DISPONIBLE ALTA INVERSION')),
    num_serie TEXT UNIQUE,
    fabricante TEXT,
    fabricacion TEXT,
    modelo TEXT,
    fabricante_engine TEXT,
    fabricante_transmision TEXT,
    puesta_marcha TEXT,
    leased_own TEXT,
    location TEXT,
    observaciones TEXT,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS historial_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    num_serie TEXT,
    status_anterior TEXT,
    status_nuevo TEXT,
    fecha_cambio TEXT DEFAULT CURRENT_TIMESTAMP,
    usuario TEXT
)
""")

conn.commit()
conn.close()

print("Base de datos y tablas creadas exitosamente.")
