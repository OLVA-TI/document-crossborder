import requests
import os
import unidecode
from dotenv import load_dotenv
load_dotenv(override=True)

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
    if not dni or dni.strip() == "":
        return {
            "exists": False,
            "match": False
        }
    
    url = f'{os.getenv("API_DNI_URL")}/dni/{dni}'
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

def sanitize_text(text):
    """ Convertir texto a mayúsculas y remover tildes """
    text = text.upper()
    text = unidecode.unidecode(text)  # Remueve tildes y otros caracteres especiales
    return text

def remove_company_types(words):
    """ Eliminar palabras comunes de tipos de empresas en Perú """
    company_types = {'SAC', 'S.A.C.', 'EIRL', 'E.I.R.L.', 'S.A.', 'SA'}
    return [word for word in words if word not in company_types]

def compare_names(name_a, name_b):
    """ Comparar dos nombres de empresas según las reglas especificadas """
    # Sanitizar ambos nombres
    name_a = sanitize_text(name_a)
    name_b = sanitize_text(name_b)

    # Convertir nombres en listas de palabras y eliminar tipos de compañías
    words_a = remove_company_types(name_a.split())
    words_b = remove_company_types(name_b.split())

    # Comparar si al menos dos palabras coinciden
    match_count = sum(1 for word in words_b if word in words_a)
    return match_count >= 2