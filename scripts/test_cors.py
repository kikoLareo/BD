#!/usr/bin/env python3
"""
Script para probar la configuración CORS de un endpoint.
"""

import os
import sys
import argparse
import json
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

# Cargar variables de entorno si existe un archivo .env
load_dotenv()

def test_cors(url, origin=None, credentials=True, verbose=False):
    """
    Prueba la configuración CORS de un endpoint.
    
    Args:
        url (str): URL del endpoint a probar
        origin (str): Origen desde el que se realiza la solicitud
        credentials (bool): Si es True, incluye credenciales en la solicitud
        verbose (bool): Si es True, muestra información detallada
    
    Returns:
        bool: True si la configuración CORS es correcta, False en caso contrario
    """
    # Si no se proporciona un origen, usar el origen de la URL
    if not origin:
        parsed_url = urlparse(url)
        origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    print(f"\n🔍 Probando configuración CORS:")
    print(f"  URL: {url}")
    print(f"  Origen: {origin}")
    print(f"  Credenciales: {'Sí' if credentials else 'No'}")
    
    # Configuración de headers para la solicitud OPTIONS (preflight)
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, Authorization"
    }
    
    if verbose:
        print(f"\n📝 Headers para la solicitud OPTIONS:")
        print(json.dumps(headers, indent=2))
    
    try:
        # Realizar la solicitud OPTIONS (preflight)
        response = requests.options(url, headers=headers)
        
        # Obtener el código de estado
        status_code = response.status_code
        print(f"\n📊 Código de estado (OPTIONS): {status_code}")
        
        # Verificar los headers de respuesta
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
            "Access-Control-Max-Age": response.headers.get("Access-Control-Max-Age")
        }
        
        print("\n📋 Headers CORS en la respuesta:")
        for key, value in cors_headers.items():
            if value:
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: ❌ No presente")
        
        # Mostrar todos los headers si es verbose
        if verbose:
            print("\n📋 Todos los headers de respuesta:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
        
        # Verificar si la configuración CORS es correcta
        allow_origin = cors_headers["Access-Control-Allow-Origin"]
        allow_credentials = cors_headers["Access-Control-Allow-Credentials"]
        
        cors_ok = True
        
        if not allow_origin:
            print("\n❌ El header Access-Control-Allow-Origin no está presente en la respuesta.")
            cors_ok = False
        elif allow_origin != origin and allow_origin != "*":
            print(f"\n❌ El header Access-Control-Allow-Origin ({allow_origin}) no coincide con el origen solicitado ({origin}).")
            cors_ok = False
        
        if credentials and not allow_credentials:
            print("\n❌ El header Access-Control-Allow-Credentials no está presente en la respuesta, pero se están usando credenciales.")
            cors_ok = False
        elif credentials and allow_credentials.lower() != "true":
            print(f"\n❌ El header Access-Control-Allow-Credentials ({allow_credentials}) no es 'true', pero se están usando credenciales.")
            cors_ok = False
        
        if credentials and allow_origin == "*":
            print("\n❌ El header Access-Control-Allow-Origin es '*', lo cual no es compatible con credenciales.")
            cors_ok = False
        
        # Ahora probar una solicitud POST real
        print("\n🔄 Probando solicitud POST real...")
        
        # Configuración de headers para la solicitud POST
        post_headers = {
            "Origin": origin,
            "Content-Type": "application/json"
        }
        
        # Datos para la solicitud POST
        data = {
            "username": "test_user",
            "password": "test_password"
        }
        
        # Realizar la solicitud POST
        response = requests.post(
            url, 
            headers=post_headers,
            json=data,
            allow_redirects=False,
            timeout=10
        )
        
        # Obtener el código de estado
        status_code = response.status_code
        print(f"\n📊 Código de estado (POST): {status_code}")
        
        # Verificar los headers CORS en la respuesta
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
            "Access-Control-Expose-Headers": response.headers.get("Access-Control-Expose-Headers")
        }
        
        print("\n📋 Headers CORS en la respuesta POST:")
        for key, value in cors_headers.items():
            if value:
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: ❌ No presente")
        
        # Verificar si la configuración CORS es correcta para la solicitud POST
        allow_origin = cors_headers["Access-Control-Allow-Origin"]
        allow_credentials = cors_headers["Access-Control-Allow-Credentials"]
        
        if not allow_origin:
            print("\n❌ El header Access-Control-Allow-Origin no está presente en la respuesta POST.")
            cors_ok = False
        elif allow_origin != origin and allow_origin != "*":
            print(f"\n❌ El header Access-Control-Allow-Origin ({allow_origin}) no coincide con el origen solicitado ({origin}).")
            cors_ok = False
        
        if credentials and not allow_credentials:
            print("\n❌ El header Access-Control-Allow-Credentials no está presente en la respuesta POST, pero se están usando credenciales.")
            cors_ok = False
        elif credentials and allow_credentials.lower() != "true":
            print(f"\n❌ El header Access-Control-Allow-Credentials ({allow_credentials}) no es 'true', pero se están usando credenciales.")
            cors_ok = False
        
        if credentials and allow_origin == "*":
            print("\n❌ El header Access-Control-Allow-Origin es '*', lo cual no es compatible con credenciales.")
            cors_ok = False
        
        if cors_ok:
            print("\n✅ La configuración CORS parece correcta.")
        else:
            print("\n❌ La configuración CORS tiene problemas.")
        
        return cors_ok
    
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Error de conexión: No se pudo conectar a {url}")
        print(f"📝 Detalles: {str(e)}")
        return False
    
    except requests.exceptions.Timeout as e:
        print(f"\n⏱️ Error de timeout: La solicitud a {url} tardó demasiado")
        print(f"📝 Detalles: {str(e)}")
        return False
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error en la solicitud: {str(e)}")
        return False

def diagnose_cors_issues(url, origin, credentials):
    """
    Diagnostica problemas comunes con CORS.
    
    Args:
        url (str): URL del endpoint
        origin (str): Origen desde el que se realiza la solicitud
        credentials (bool): Si se están usando credenciales
    """
    print("\n🔍 Diagnóstico de problemas con CORS:")
    
    # Verificar la URL
    print("\n1️⃣ Verificando la URL...")
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            print(f"❌ La URL {url} no es válida.")
            print("  - Asegúrate de incluir el protocolo (http:// o https://).")
            print("  - Verifica que la URL sea correcta.")
        else:
            print(f"✅ La URL {url} parece válida.")
    except Exception:
        print(f"❌ La URL {url} no es válida.")
    
    # Verificar el origen
    print("\n2️⃣ Verificando el origen...")
    try:
        parsed_origin = urlparse(origin)
        if not parsed_origin.scheme or not parsed_origin.netloc:
            print(f"❌ El origen {origin} no es válido.")
            print("  - Asegúrate de incluir el protocolo (http:// o https://).")
            print("  - Verifica que el origen sea correcto.")
        else:
            print(f"✅ El origen {origin} parece válido.")
    except Exception:
        print(f"❌ El origen {origin} no es válido.")
    
    # Verificar credenciales
    print("\n3️⃣ Verificando credenciales...")
    if credentials:
        print("ℹ️ Estás usando credenciales en la solicitud.")
        print("  - Asegúrate de que el servidor tenga configurado Access-Control-Allow-Credentials: true")
        print("  - El servidor NO PUEDE usar Access-Control-Allow-Origin: * cuando se usan credenciales.")
        print("  - El servidor DEBE especificar el origen exacto en Access-Control-Allow-Origin.")
    else:
        print("ℹ️ No estás usando credenciales en la solicitud.")
        print("  - El servidor puede usar Access-Control-Allow-Origin: * si no necesita distinguir entre orígenes.")
    
    # Recomendaciones para FastAPI
    print("\n4️⃣ Recomendaciones para FastAPI:")
    print("  - Verifica la configuración CORS en main.py:")
    print("    ```python")
    print("    app.add_middleware(")
    print("        CORSMiddleware,")
    if credentials:
        print(f"        allow_origins=['{origin}'],  # NO uses '*' con credenciales")
    else:
        print("        allow_origins=['*'],  # O lista de orígenes específicos")
    print("        allow_credentials=True,")
    print("        allow_methods=['*'],")
    print("        allow_headers=['*'],")
    print("    )")
    print("    ```")
    
    # Recomendaciones generales
    print("\n5️⃣ Recomendaciones generales:")
    print("  - Si estás usando un proxy o balanceador de carga, asegúrate de que esté configurado para pasar los headers CORS.")
    print("  - Verifica que no haya middleware o código que esté modificando los headers CORS.")
    print("  - Si estás usando credenciales, asegúrate de que el navegador esté configurado para enviarlas.")
    print("  - Prueba con diferentes navegadores para descartar problemas específicos del navegador.")
    print("  - Considera usar una herramienta como CORS Anywhere para depurar problemas de CORS.")

def main():
    parser = argparse.ArgumentParser(description="Prueba la configuración CORS de un endpoint")
    parser.add_argument("--url", default=os.getenv("API_URL", "http://localhost:8000/api/auth/login"),
                        help="URL del endpoint a probar (default: http://localhost:8000/api/auth/login)")
    parser.add_argument("--origin", default=None,
                        help="Origen desde el que se realiza la solicitud (default: derivado de la URL)")
    parser.add_argument("--credentials", action="store_true", default=True,
                        help="Incluir credenciales en la solicitud (default: True)")
    parser.add_argument("--no-credentials", action="store_false", dest="credentials",
                        help="No incluir credenciales en la solicitud")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Muestra información detallada")
    
    args = parser.parse_args()
    
    success = test_cors(args.url, args.origin, args.credentials, args.verbose)
    
    if not success:
        diagnose_cors_issues(args.url, args.origin or urlparse(args.url).netloc, args.credentials)
        sys.exit(1)

if __name__ == "__main__":
    main()
