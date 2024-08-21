import requests
import os

def additional_validation(dni_data, consignado):
    # Extraer nombres y apellidos del DNI
    nombres_api = dni_data['nombres'].split()
    apellido_paterno = dni_data['apellidoPaterno']
    apellido_materno = dni_data['apellidoMaterno']

    # Dividir los datos consignados en palabras
    consignado_parts = consignado.lower().split()

    # Verificar si al menos un nombre y un apellido coinciden
    match_nombre = any(nombre.lower() in consignado_parts for nombre in nombres_api)
    match_apellido = apellido_paterno.lower() in consignado_parts or apellido_materno.lower() in consignado_parts

    if match_nombre and match_apellido:
        return True
    else:
        return False

def validate_dni(dni, consignado):
    url = os.getenv("API_DNI_URL") + dni
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()["data"]
        full_name = f"{data['nombres']} {data['apellidoPaterno']} {data['apellidoMaterno']}"
        match = additional_validation(data, consignado)
        return {
            "exists": True,
            "match": match,
            "full_name": full_name,
            "data": data
        }
    elif response.status_code == 204:
        return {
            "exists": False,
            "match": False
        }
    else:
        response.raise_for_status()
