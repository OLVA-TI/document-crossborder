import requests
import unidecode
import os
from dotenv import load_dotenv
load_dotenv(override=True)

def handle_ruc20_validation(cursor, ruc, tipo_doc, consignado, emision, remito):
    # Consultar la API externa
    api_url = f'{os.getenv("API_DNI_URL")}/ruc/{ruc}'
    response = requests.get(api_url)

    if response.status_code == 200:
        ruc_data = response.json().get('data')
        if ruc_data:
            razonsocial = ruc_data['nombre_o_razon_social']
            estado = ruc_data['estado']
            condicion = ruc_data['condicion']

            # Comparar nombres
            match = compare_names(razonsocial, consignado)
            if match:
                if estado == 'ACTIVO' and condicion == 'HABIDO':
                    cursor.execute("""
                        UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
                        SET ID_ESTADO_CONSIGNADO = 9005,
                            CONSIGNADO = :consignado,
                            CONSIGNADO_OLD = :consignado_old,
                            NRO_DOC_IDENTIDAD = :nro_doc,
                            NRO_DOC_IDENTIDAD_OLD = :nro_doc,
                            TIPO_DOC_IDENTIDAD = :tipo_doc,
                            TIPO_DOC_IDENTIDAD_OLD = :tipo_doc
                        WHERE emision = :emision AND remito = :remito
                    """, {'consignado': razonsocial, 'consignado_old': consignado, 'emision': emision, 'remito': remito, 'nro_doc': ruc, 'tipo_doc': tipo_doc})
                    print(f"RUC {ruc} ACTIVO Y HABIDO.")
                else:
                    obs = f"ESTADO: {estado}, CONDICIÓN: {condicion}"
                    cursor.execute("""
                        UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
                        SET ID_ESTADO_CONSIGNADO = 9006,
                            ID_MOTIVO_CONSIGNADO = 9009,
                            OBS_VALIDACION_CONSIGNADO = :obs,
                            CONSIGNADO = :consignado,
                            CONSIGNADO_OLD = :consignado,
                            NRO_DOC_IDENTIDAD = :nro_doc,
                            NRO_DOC_IDENTIDAD_OLD = :nro_doc,
                            TIPO_DOC_IDENTIDAD = :tipo_doc,
                            TIPO_DOC_IDENTIDAD_OLD = :tipo_doc
                        WHERE emision = :emision AND remito = :remito
                    """, {'obs': obs, 'consignado': consignado, 'emision': emision, 'remito': remito, 'nro_doc': ruc, 'tipo_doc': tipo_doc})
                    print(f"RUC {ruc} NO ACTIVO O HABIDO.")
            else:
                obs = f"RUC NO MATCH: {ruc} RAZON SOCIAL: {razonsocial}"
                cursor.execute("""
                    UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
                    SET ID_ESTADO_CONSIGNADO = 9006,
                        ID_MOTIVO_CONSIGNADO = 9011,
                        OBS_VALIDACION_CONSIGNADO = :obs
                    WHERE emision = :emision AND remito = :remito
                """, {'obs': obs, 'emision': emision, 'remito': remito})
                print(f"RUC {ruc} NO MATCH.")
        else:
            handle_missing_ruc(cursor, ruc, emision, remito)
    elif response.status_code == 204:
        handle_missing_ruc(cursor, ruc, emision, remito)
    else:
        print(f"Error al consultar la API para el RUC {ruc}: {response.status_code}")

def handle_missing_ruc(cursor, ruc, emision, remito):
    obs = f"RUC NO EXISTE: {ruc}"
    cursor.execute("""
        UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
        SET ID_ESTADO_CONSIGNADO = 9006,
            ID_MOTIVO_CONSIGNADO = 9010,
            OBS_VALIDACION_CONSIGNADO = :obs
        WHERE emision = :emision AND remito = :remito
    """, {'obs': obs, 'emision': emision, 'remito': remito})
    print(f"RUC {ruc} NO EXISTE.")

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
