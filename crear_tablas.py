# crear_tablas.py
import sqlite3

DB = "data/plantlist.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

# Tabla DieselTractoplanas
c.execute("""
CREATE TABLE IF NOT EXISTS DieselTractoplanas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha_hora TEXT NOT NULL
)
""")

# Tabla DieselLlenos
c.execute("""
CREATE TABLE IF NOT EXISTS DieselLlenos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha_hora TEXT NOT NULL
)
""")

# Tabla DieselVacios
c.execute("""
CREATE TABLE IF NOT EXISTS DieselVacios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha_hora TEXT NOT NULL
)
""")

# Tabla DieselMarco
c.execute("""
CREATE TABLE IF NOT EXISTS DieselMarco (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha_hora TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Tablas creadas correctamente.")
