import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="waveshub_db",
        user="postgres",
        password="WavesHub"
    )
    print("Conexión exitosa a la base de datos.")
    conn.close()
except Exception as e:
    print(f"Ocurrió un error al conectar: {repr(e)}")
