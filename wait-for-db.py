#!/usr/bin/env python3
"""
Script simple para esperar que la base de datos esté disponible
antes de iniciar la aplicación Flask.
"""
import time
import socket
import sys
import subprocess

def wait_for_port(host, port, timeout=60):
    """Espera a que un puerto esté disponible"""
    print(f"Esperando que {host}:{port} esté disponible...")
    start_time = time.time()
    
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {host}:{port} está disponible!")
                return True
                
        except socket.error:
            pass
        
        if time.time() - start_time > timeout:
            print(f"❌ Timeout esperando {host}:{port}")
            return False
            
        print(f"⏳ Esperando {host}:{port}...")
        time.sleep(2)

def main():
    # Esperar a que la base de datos esté disponible
    if not wait_for_port('db', 3306, 60):
        print("❌ No se pudo conectar a la base de datos")
        sys.exit(1)
    
    # Iniciar la aplicación Flask
    print("🚀 Iniciando aplicación Flask...")
    try:
        subprocess.run([sys.executable, 'run.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
