"""
Script para crear un administrador en la colección "Administradores" de MongoDB Atlas.
El password se pide de forma segura (no queda visible en pantalla ni en el historial)
y se guarda hasheado con bcrypt.

Uso:
    python crear_admin.py
"""

import os
import sys
from getpass import getpass

import bcrypt
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure


# --- Configuración ---
# Podés pasar la URI de Atlas por variable de entorno o pegarla directo acá.
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://usuario:password@cluster0.5baogof.mongodb.net/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "UbiLife")
COLLECTION_NAME = "Administradores"
ADMIN_EMAIL = "admin@gmail.com"


def main():
    # 1. Pedir el password de forma segura (no se muestra en pantalla)
    password = getpass("Ingresa el password para el admin: ")
    password_confirm = getpass("Confirma el password: ")

    if password != password_confirm:
        print("❌ Los passwords no coinciden. Abortando.")
        sys.exit(1)

    if len(password) < 8:
        print("⚠️  El password tiene menos de 8 caracteres, se recomienda uno más largo.")
        confirmar = input("¿Continuar de todas formas? (s/n): ")
        if confirmar.lower() != "s":
            sys.exit(1)

    # 2. Hashear el password con bcrypt
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    # 3. Conectarse a MongoDB Atlas
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Forzar la conexión para detectar errores temprano
        client.admin.command("ping")
    except ConnectionFailure as e:
        print(f"❌ No se pudo conectar a MongoDB: {e}")
        sys.exit(1)

    db = client[DATABASE_NAME]
    coleccion = db[COLLECTION_NAME]

    # 4. Verificar si ya existe un admin con ese correo
    existente = coleccion.find_one({"correo": ADMIN_EMAIL})
    if existente:
        print(f"⚠️  Ya existe un administrador con el correo {ADMIN_EMAIL}.")
        sobrescribir = input("¿Deseas sobrescribir el password? (s/n): ")
        if sobrescribir.lower() != "s":
            print("Cancelado.")
            client.close()
            sys.exit(0)

        coleccion.update_one(
            {"correo": ADMIN_EMAIL},
            {"$set": {"password": hashed_password}}
        )
        print(f"✅ Password actualizado para {ADMIN_EMAIL}.")
    else:
        # 5. Insertar el nuevo administrador
        try:
            documento = {
                "correo": ADMIN_EMAIL,
                "password": hashed_password,  # se guarda como bytes; PyMongo lo almacena como BSON Binary
            }
            resultado = coleccion.insert_one(documento)
            print(f"✅ Administrador creado con éxito. ID: {resultado.inserted_id}")
        except OperationFailure as e:
            print(f"❌ Error al insertar en MongoDB: {e}")
            client.close()
            sys.exit(1)

    client.close()


if __name__ == "__main__":
    main()