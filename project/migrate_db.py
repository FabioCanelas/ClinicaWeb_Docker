"""
Script para actualizar la base de datos con nuevos campos del modelo Usuario
Ejecutar este script para agregar los campos: estado, fecha_creacion, ultimo_acceso, cambiar_contrasena
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extensions import db
from src.app import create_app
from datetime import datetime
import sqlalchemy as sa

def actualizar_base_datos():
    """
    Actualiza la base de datos agregando los nuevos campos al modelo Usuario
    """
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Verificando estructura actual de la tabla usuarios...")
            
            # Verificar si las columnas ya existen
            inspector = sa.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('usuarios')]
            print(f"Columnas actuales: {columns}")
            
            # Lista de nuevas columnas a agregar con sus definiciones SQL
            nuevas_columnas = {
                'estado': 'BOOLEAN NOT NULL DEFAULT TRUE',
                'fecha_creacion': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                'ultimo_acceso': 'DATETIME NULL',
                'cambiar_contrasena': 'BOOLEAN NOT NULL DEFAULT FALSE'
            }
            
            columnas_agregadas = []
            
            for columna, definicion in nuevas_columnas.items():
                if columna not in columns:
                    try:
                        # Construir la consulta SQL para agregar la columna
                        sql = f"ALTER TABLE usuarios ADD COLUMN {columna} {definicion}"
                        print(f"📝 Ejecutando: {sql}")
                        
                        # Ejecutar la consulta
                        with db.engine.connect() as connection:
                            result = connection.execute(sa.text(sql))
                            connection.commit()
                        
                        columnas_agregadas.append(columna)
                        print(f"✅ Columna '{columna}' agregada exitosamente")
                    except Exception as e:
                        print(f"❌ Error agregando columna '{columna}': {e}")
                        # Continuar con las demás columnas
                else:
                    print(f"ℹ️  Columna '{columna}' ya existe")
            
            if columnas_agregadas:
                print(f"\n🔄 Actualizando registros existentes...")
                
                # Actualizar usuarios existentes con valores por defecto si es necesario
                try:
                    # Para usuarios que no tienen estado definido, establecer como TRUE
                    update_sql = """
                    UPDATE usuarios 
                    SET estado = TRUE 
                    WHERE estado IS NULL
                    """
                    with db.engine.connect() as connection:
                        connection.execute(sa.text(update_sql))
                        connection.commit()
                    
                    # Para usuarios que no tienen fecha_creacion, usar la fecha actual
                    update_sql2 = """
                    UPDATE usuarios 
                    SET fecha_creacion = NOW() 
                    WHERE fecha_creacion IS NULL
                    """
                    with db.engine.connect() as connection:
                        connection.execute(sa.text(update_sql2))
                        connection.commit()
                    
                    # Para usuarios que no tienen cambiar_contrasena definido, establecer como FALSE
                    update_sql3 = """
                    UPDATE usuarios 
                    SET cambiar_contrasena = FALSE 
                    WHERE cambiar_contrasena IS NULL
                    """
                    with db.engine.connect() as connection:
                        connection.execute(sa.text(update_sql3))
                        connection.commit()
                    
                    print("✅ Registros existentes actualizados correctamente")
                    
                except Exception as e:
                    print(f"⚠️  Error actualizando registros existentes: {e}")
            
            # Verificar la estructura final
            print("\n🔍 Verificando estructura final...")
            columns_final = [col['name'] for col in inspector.get_columns('usuarios')]
            print(f"Columnas finales: {columns_final}")
            
            print("\n🎉 Migración completada exitosamente!")
            print("\n💡 Ahora puedes reiniciar la aplicación para usar las nuevas funcionalidades.")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            print("🔧 Revisa la conexión a la base de datos y los permisos")

if __name__ == "__main__":
    print("🚀 Iniciando migración de base de datos...")
    print("⚠️  Asegúrate de que la aplicación esté detenida antes de continuar")
    
    respuesta = input("¿Continuar con la migración? (s/N): ")
    if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        actualizar_base_datos()
    else:
        print("❌ Migración cancelada")
