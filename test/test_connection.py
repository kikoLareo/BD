import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="wavestudio_db",
        user="kiko",
        password=".,Franlareo1701_.,"
    )
    print("Conexión exitosa a la base de datos.")
    conn.close()
except Exception as e:
    print(f"Ocurrió un error al conectar: {repr(e)}")
