#!/usr/bin/env python3
"""
Script para probar la generación y validación de tokens JWT.
"""

import os
import sys
import argparse
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno si existe un archivo .env
load_dotenv()

def test_jwt_generation(secret_key=None, algorithm=None, verbose=False):
    """
    Prueba la generación y validación de tokens JWT.
    
    Args:
        secret_key (str): Clave secreta para firmar el token
        algorithm (str): Algoritmo de firma (por defecto HS256)
        verbose (bool): Si es True, muestra información detallada
    
    Returns:
        bool: True si la generación y validación son exitosas, False en caso contrario
    """
    try:
        from jose import jwt, JWTError
    except ImportError:
        print("❌ Error: No se pudo importar python-jose")
        print("Por favor, instálalo con: pip install python-jose[cryptography]")
        return False
    
    # Usar valores por defecto si no se proporcionan
    secret_key = secret_key or os.getenv("SECRET_KEY", "your_secret_key_here_change_this_in_production")
    algorithm = algorithm or os.getenv("ALGORITHM", "HS256")
    
    print(f"\n🔍 Probando generación y validación de tokens JWT:")
    print(f"  Clave secreta: {'*' * len(secret_key)}")
    print(f"  Algoritmo: {algorithm}")
    
    # Datos de prueba para el token
    test_data = {
        "sub": "test_user",
        "user_id": 1,
        "email": "test@example.com",
        "roles": [1, 2],
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    
    if verbose:
        print(f"\n📝 Datos para el token:")
        print(json.dumps(test_data, indent=2, default=str))
    
    try:
        # Generar token
        token = jwt.encode(test_data, secret_key, algorithm=algorithm)
        print(f"\n✅ Token JWT generado correctamente")
        
        if verbose:
            print(f"\n🔑 Token JWT:")
            print(token)
        else:
            print(f"🔑 Token JWT: {token[:20]}...")
        
        # Decodificar token
        try:
            decoded = jwt.decode(token, secret_key, algorithms=[algorithm])
            print(f"\n✅ Token JWT decodificado correctamente")
            
            if verbose:
                print(f"\n📋 Contenido del token decodificado:")
                print(json.dumps(decoded, indent=2))
            else:
                print(f"👤 Usuario: {decoded.get('sub', 'N/A')}")
                print(f"📧 Email: {decoded.get('email', 'N/A')}")
                print(f"🔑 Roles: {decoded.get('roles', [])}")
            
            return True
        except JWTError as e:
            print(f"\n❌ Error al decodificar el token: {str(e)}")
            return False
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        return False

def diagnose_jwt_issues(secret_key):
    """
    Diagnostica problemas comunes con JWT.
    
    Args:
        secret_key (str): Clave secreta para firmar el token
    """
    print("\n🔍 Diagnóstico de problemas con JWT:")
    
    # Verificar la clave secreta
    print("\n1️⃣ Verificando la clave secreta...")
    if not secret_key:
        print("❌ La clave secreta está vacía.")
        print("  - Asegúrate de configurar SECRET_KEY en el archivo .env o en las variables de entorno.")
    elif secret_key == "your_secret_key_here_change_this_in_production":
        print("⚠️ Estás usando la clave secreta por defecto.")
        print("  - Esto es inseguro para entornos de producción.")
        print("  - Genera una clave secreta fuerte y configúrala en el archivo .env o en las variables de entorno.")
    elif len(secret_key) < 32:
        print("⚠️ La clave secreta es demasiado corta.")
        print("  - Se recomienda usar una clave de al menos 32 caracteres para mayor seguridad.")
    else:
        print("✅ La clave secreta parece válida.")
    
    # Verificar dependencias
    print("\n2️⃣ Verificando dependencias...")
    try:
        import jose
        print(f"✅ python-jose está instalado (versión: {jose.__version__})")
    except (ImportError, AttributeError):
        print("❌ python-jose no está instalado o no se pudo determinar su versión.")
        print("  - Instálalo con: pip install python-jose[cryptography]")
    
    try:
        from cryptography.hazmat.backends import default_backend
        print("✅ cryptography está instalado")
    except ImportError:
        print("❌ cryptography no está instalado.")
        print("  - Instálalo con: pip install cryptography")
    
    # Verificar configuración en el código
    print("\n3️⃣ Verificando configuración en el código...")
    print("  - Asegúrate de que JWT/tokens.py esté importando la clave secreta correctamente:")
    print("    ```python")
    print("    SECRET_KEY = os.getenv('SECRET_KEY')")
    print("    ```")
    print("  - Verifica que el algoritmo sea compatible (normalmente HS256):")
    print("    ```python")
    print("    ALGORITHM = 'HS256'")
    print("    ```")
    
    # Recomendaciones generales
    print("\n4️⃣ Recomendaciones generales:")
    print("  - Asegúrate de que la clave secreta sea la misma en todos los entornos donde se validan los tokens.")
    print("  - Verifica que la fecha de expiración (exp) esté configurada correctamente.")
    print("  - Comprueba que los claims del token (sub, user_id, etc.) sean correctos.")
    print("  - Si estás usando múltiples instancias, asegúrate de que todas tengan la misma configuración de JWT.")

def generate_strong_key():
    """
    Genera una clave secreta fuerte para JWT.
    
    Returns:
        str: Clave secreta generada
    """
    try:
        import secrets
        key = secrets.token_hex(32)  # 64 caracteres hexadecimales (32 bytes)
        return key
    except ImportError:
        import random
        import string
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(64))

def main():
    parser = argparse.ArgumentParser(description="Prueba la generación y validación de tokens JWT")
    parser.add_argument("--secret-key", default=os.getenv("SECRET_KEY"),
                        help="Clave secreta para firmar el token (default: valor de SECRET_KEY)")
    parser.add_argument("--algorithm", default=os.getenv("ALGORITHM", "HS256"),
                        help="Algoritmo de firma (default: valor de ALGORITHM o HS256)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Muestra información detallada")
    parser.add_argument("--generate-key", action="store_true",
                        help="Genera una clave secreta fuerte")
    
    args = parser.parse_args()
    
    if args.generate_key:
        key = generate_strong_key()
        print(f"\n🔐 Clave secreta generada:")
        print(key)
        print("\nPuedes configurarla en tu archivo .env:")
        print(f"SECRET_KEY={key}")
        return
    
    success = test_jwt_generation(args.secret_key, args.algorithm, args.verbose)
    
    if not success:
        diagnose_jwt_issues(args.secret_key)
        sys.exit(1)

if __name__ == "__main__":
    main()
