#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos PostgreSQL.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
import time

# Cargar variables de entorno si existe un archivo .env
load_dotenv()

def test_connection(host, port, dbname, user, password, verbose=False):
    """
    Prueba la conexión a la base de datos PostgreSQL.
    
    Args:
        host (str): Host de la base de datos
        port (int): Puerto de la base de datos
        dbname (str): Nombre de la base de datos
        user (str): Usuario de la base de datos
        password (str): Contraseña de la base de datos
        verbose (bool): Si es True, muestra información detallada
    
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        import psycopg2
    except ImportError:
        print("❌ Error: No se pudo importar psycopg2")
        print("Por favor, instálalo con: pip install psycopg2-binary")
        return False
    
    print(f"\n🔍 Probando conexión a la base de datos PostgreSQL:")
    print(f"  Host: {host}")
    print(f"  Puerto: {port}")
    print(f"  Base de datos: {dbname}")
    print(f"  Usuario: {user}")
    print(f"  Contraseña: {'*' * len(password)}")
    
    connection_string = f"host={host} port={port} dbname={dbname} user={user} password={password}"
    
    if verbose:
        print(f"\n📝 Cadena de conexión: {connection_string}")
    
    try:
        start_time = time.time()
        conn = psycopg2.connect(connection_string)
        end_time = time.time()
        
        print(f"\n✅ Conexión exitosa! (Tiempo: {end_time - start_time:.2f} segundos)")
        
        if verbose:
            print("\n📊 Información de la conexión:")
            print(f"  Backend PID: {conn.get_backend_pid()}")
            print(f"  Codificación: {conn.encoding}")
            print(f"  Aislamiento de transacción: {conn.isolation_level}")
        
        # Probar una consulta simple
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"\n📋 Versión de PostgreSQL: {version}")
        
        # Listar tablas
        try:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            if tables:
                print("\n📚 Tablas disponibles:")
                for table in tables:
                    print(f"  - {table[0]}")
                
                # Verificar si existe la tabla users
                if any(table[0] == 'users' for table in tables):
                    print("\n👤 Verificando tabla 'users'...")
                    cursor.execute("SELECT COUNT(*) FROM users;")
                    user_count = cursor.fetchone()[0]
                    print(f"  - Número de usuarios: {user_count}")
                    
                    if user_count > 0 and verbose:
                        cursor.execute("SELECT id, username, email FROM users LIMIT 5;")
                        users = cursor.fetchall()
                        print("\n👥 Primeros 5 usuarios:")
                        for user in users:
                            print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
            else:
                print("\n⚠️ No se encontraron tablas en la base de datos.")
        except Exception as e:
            print(f"\n⚠️ No se pudieron listar las tablas: {str(e)}")
        
        cursor.close()
        conn.close()
        print("\n🔒 Conexión cerrada correctamente.")
        return True
    
    except psycopg2.OperationalError as e:
        print(f"\n❌ Error de conexión: {str(e)}")
        return False
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        return False

def diagnose_connection_error(host, port, dbname, user, password):
    """
    Diagnostica problemas comunes de conexión a la base de datos.
    
    Args:
        host (str): Host de la base de datos
        port (int): Puerto de la base de datos
        dbname (str): Nombre de la base de datos
        user (str): Usuario de la base de datos
        password (str): Contraseña de la base de datos
    """
    print("\n🔍 Diagnóstico de problemas de conexión:")
    
    # Verificar si el host es accesible
    print("\n1️⃣ Verificando si el host es accesible...")
    import socket
    try:
        socket.create_connection((host, port), timeout=5)
        print(f"✅ El host {host} es accesible en el puerto {port}.")
    except socket.timeout:
        print(f"❌ Timeout al conectar a {host}:{port}.")
        print("  - Verifica que el servidor de base de datos esté en ejecución.")
        print("  - Comprueba que el firewall permita conexiones al puerto especificado.")
    except socket.error as e:
        print(f"❌ No se pudo conectar a {host}:{port}: {str(e)}")
        print("  - Verifica que la dirección del host sea correcta.")
        print("  - Comprueba que el puerto sea el correcto (normalmente 5432 para PostgreSQL).")
        print("  - Asegúrate de que el servidor de base de datos esté en ejecución.")
        print("  - Verifica que el firewall permita conexiones al puerto especificado.")
    
    # Verificar credenciales
    print("\n2️⃣ Verificando credenciales...")
    if not user or not password:
        print("❌ Usuario o contraseña vacíos.")
        print("  - Asegúrate de proporcionar un usuario y contraseña válidos.")
    else:
        print("✅ Usuario y contraseña proporcionados.")
    
    # Verificar nombre de la base de datos
    print("\n3️⃣ Verificando nombre de la base de datos...")
    if not dbname:
        print("❌ Nombre de la base de datos vacío.")
        print("  - Asegúrate de proporcionar un nombre de base de datos válido.")
    else:
        print(f"✅ Nombre de base de datos proporcionado: {dbname}")
    
    # Verificar si es una instancia RDS
    if "rds.amazonaws.com" in host:
        print("\n4️⃣ Detectada instancia RDS de AWS...")
        print("  - Verifica que el grupo de seguridad de la instancia RDS permita conexiones desde tu IP.")
        print("  - Comprueba que la instancia RDS esté en estado 'available'.")
        print("  - Asegúrate de que la instancia EC2 y la instancia RDS estén en la misma VPC o tengan conectividad.")
    
    # Verificar si es un contenedor Docker
    if host == "db" or host == "postgres" or host == "postgresql":
        print("\n4️⃣ Posible uso de Docker detectado...")
        print("  - Si estás usando Docker, asegúrate de que los contenedores estén en la misma red.")
        print("  - Verifica que el contenedor de la base de datos esté en ejecución.")
        print("  - Comprueba que el nombre del host coincida con el nombre del servicio en docker-compose.yml.")
    
    print("\n5️⃣ Recomendaciones generales:")
    print("  - Verifica la cadena de conexión en el archivo .env o en las variables de entorno.")
    print("  - Asegúrate de que la base de datos exista. Puedes crearla con: CREATE DATABASE nombre_db;")
    print("  - Comprueba que el usuario tenga permisos para acceder a la base de datos.")
    print("  - Si estás usando un proxy o VPN, verifica que no esté bloqueando la conexión.")
    print("  - Reinicia el servidor de base de datos si es posible.")

def main():
    parser = argparse.ArgumentParser(description="Prueba la conexión a la base de datos PostgreSQL")
    parser.add_argument("--host", default=os.getenv("DB_HOST", "localhost"),
                        help="Host de la base de datos (default: valor de DB_HOST o localhost)")
    parser.add_argument("--port", type=int, default=int(os.getenv("DB_PORT", "5432")),
                        help="Puerto de la base de datos (default: valor de DB_PORT o 5432)")
    parser.add_argument("--dbname", default=os.getenv("DB_NAME", "wavestudio_db"),
                        help="Nombre de la base de datos (default: valor de DB_NAME o wavestudio_db)")
    parser.add_argument("--user", default=os.getenv("DB_USER", "kiko"),
                        help="Usuario de la base de datos (default: valor de DB_USER o kiko)")
    parser.add_argument("--password", default=os.getenv("DB_PASSWORD", ""),
                        help="Contraseña de la base de datos (default: valor de DB_PASSWORD)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Muestra información detallada")
    
    args = parser.parse_args()
    
    # Si no se proporciona contraseña, solicitarla
    if not args.password:
        import getpass
        args.password = getpass.getpass("Contraseña de la base de datos: ")
    
    success = test_connection(args.host, args.port, args.dbname, args.user, args.password, args.verbose)
    
    if not success:
        diagnose_connection_error(args.host, args.port, args.dbname, args.user, args.password)
        sys.exit(1)

if __name__ == "__main__":
    main()
