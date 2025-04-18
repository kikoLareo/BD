#!/usr/bin/env python3
"""
Script para probar el endpoint de login y diagnosticar problemas.
"""

import requests
import json
import sys
import argparse
import os
from dotenv import load_dotenv

# Cargar variables de entorno si existe un archivo .env
load_dotenv()

def test_login(url, username, password, verbose=False):
    """
    Prueba el endpoint de login con las credenciales proporcionadas.
    
    Args:
        url (str): URL completa del endpoint de login
        username (str): Nombre de usuario
        password (str): Contraseña
        verbose (bool): Si es True, muestra información detallada
    
    Returns:
        dict: Respuesta del servidor
    """
    print(f"\n🔍 Probando login en: {url}")
    print(f"👤 Usuario: {username}")
    print(f"🔑 Contraseña: {'*' * len(password)}")
    
    # Datos para la solicitud
    data = {
        "username": username,
        "password": password
    }
    
    if verbose:
        print(f"\n📤 Enviando datos: {json.dumps(data, indent=2)}")
    
    # Configuración de headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    if verbose:
        print(f"📋 Headers: {json.dumps(headers, indent=2)}")
    
    try:
        # Realizar la solicitud
        response = requests.post(url, json=data, headers=headers)
        
        # Obtener el código de estado
        status_code = response.status_code
        print(f"\n📊 Código de estado: {status_code}")
        
        # Intentar obtener el cuerpo de la respuesta como JSON
        try:
            response_json = response.json()
            if verbose:
                print(f"📥 Respuesta: {json.dumps(response_json, indent=2)}")
            else:
                if status_code == 200:
                    print("✅ Login exitoso!")
                    print(f"🔑 Token: {response_json.get('access_token', '')[:20]}...")
                    if 'user' in response_json:
                        print(f"👤 Usuario: {response_json['user'].get('username', '')}")
                        print(f"📧 Email: {response_json['user'].get('email', '')}")
                        print(f"🔑 Roles: {response_json['user'].get('roles', [])}")
                else:
                    print(f"❌ Error: {response_json.get('detail', {}).get('message', 'Desconocido')}")
                    print(f"📝 Detalles: {response_json.get('detail', {}).get('details', 'Sin detalles')}")
        except json.JSONDecodeError:
            print("⚠️ La respuesta no es un JSON válido")
            print(f"📄 Contenido: {response.text[:500]}")
        
        # Mostrar headers de la respuesta si es verbose
        if verbose:
            print("\n📋 Headers de respuesta:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
        
        return {
            "status_code": status_code,
            "response": response_json if 'response_json' in locals() else response.text,
            "headers": dict(response.headers)
        }
    
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Error de conexión: No se pudo conectar a {url}")
        print(f"📝 Detalles: {str(e)}")
        return {"error": "connection_error", "details": str(e)}
    
    except requests.exceptions.Timeout as e:
        print(f"⏱️ Error de timeout: La solicitud a {url} tardó demasiado")
        print(f"📝 Detalles: {str(e)}")
        return {"error": "timeout", "details": str(e)}
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la solicitud: {str(e)}")
        return {"error": "request_error", "details": str(e)}

def diagnose_error(result):
    """
    Diagnostica el error basado en el resultado de la prueba.
    
    Args:
        result (dict): Resultado de la prueba
    """
    if "error" in result:
        if result["error"] == "connection_error":
            print("\n🔍 Diagnóstico:")
            print("  - Verifica que el servidor esté en ejecución")
            print("  - Comprueba que la URL sea correcta")
            print("  - Asegúrate de que no haya un firewall bloqueando la conexión")
            print("  - Verifica que el puerto esté abierto")
        elif result["error"] == "timeout":
            print("\n🔍 Diagnóstico:")
            print("  - El servidor podría estar sobrecargado")
            print("  - La base de datos podría estar tardando en responder")
            print("  - Verifica la conectividad de red")
        return
    
    status_code = result.get("status_code")
    
    if status_code == 200:
        print("\n🔍 Diagnóstico: Todo funciona correctamente")
        return
    
    print("\n🔍 Diagnóstico:")
    
    if status_code == 400:
        print("  - La solicitud tiene un formato incorrecto")
        print("  - Verifica que los campos 'username' y 'password' estén presentes")
        print("  - Asegúrate de que el Content-Type sea 'application/json'")
    
    elif status_code == 401:
        print("  - Credenciales inválidas")
        print("  - Verifica que el usuario exista en la base de datos")
        print("  - Comprueba que la contraseña sea correcta")
    
    elif status_code == 403:
        print("  - No tienes permiso para acceder a este recurso")
        print("  - Verifica los roles del usuario")
    
    elif status_code == 404:
        print("  - El endpoint no existe")
        print("  - Verifica la URL")
        print("  - Comprueba que el router esté registrado correctamente")
    
    elif status_code == 500:
        print("  - Error interno del servidor")
        print("  - Verifica los logs del servidor para más detalles")
        print("  - Posibles causas:")
        print("    * Problema de conexión a la base de datos")
        print("    * Error en la generación del token JWT")
        print("    * Excepción no manejada en el código")
        print("    * Problema con la configuración CORS")
        print("\n  Recomendaciones:")
        print("    * Ejecuta el servidor con nivel de log DEBUG")
        print("    * Verifica la conexión a la base de datos")
        print("    * Comprueba que la clave secreta JWT esté configurada correctamente")
        print("    * Revisa la configuración CORS si estás usando credenciales")
    
    elif status_code == 502 or status_code == 503 or status_code == 504:
        print("  - Problema con el servidor o proxy")
        print("  - Verifica que el servidor esté en ejecución")
        print("  - Comprueba la configuración del proxy o balanceador de carga")
    
    else:
        print(f"  - Código de estado no reconocido: {status_code}")
        print("  - Verifica los logs del servidor para más detalles")

def main():
    parser = argparse.ArgumentParser(description="Prueba el endpoint de login y diagnostica problemas")
    parser.add_argument("--url", default=os.getenv("API_URL", "http://localhost:8000/api/auth/login"),
                        help="URL del endpoint de login (default: http://localhost:8000/api/auth/login)")
    parser.add_argument("--username", default=os.getenv("TEST_USERNAME", "admin@wavestudio.com"),
                        help="Nombre de usuario (default: admin@wavestudio.com)")
    parser.add_argument("--password", default=os.getenv("TEST_PASSWORD", "admin123"),
                        help="Contraseña (default: admin123)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Muestra información detallada")
    
    args = parser.parse_args()
    
    result = test_login(args.url, args.username, args.password, args.verbose)
    diagnose_error(result)

if __name__ == "__main__":
    main()
