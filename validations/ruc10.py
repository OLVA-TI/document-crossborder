import requests
import os
from dotenv import load_dotenv
load_dotenv(override=True)

def handle_ruc10_validation(cursor, ruc, tipo_doc, nro_doc, consignado, emision, remito, validate=True):
    # Consultar la API externa
    api_url = f'{os.getenv("API_DNI_URL")}/ruc/{ruc}'
    response = requests.get(api_url)

    if response.status_code == 200:
        ruc_data = response.json().get('data')
        if ruc_data:
            razonsocial = ruc_data['nombre_o_razon_social']
            estado = ruc_data['estado']
            condicion = ruc_data['condicion']

            if estado == 'ACTIVO' and condicion == 'HABIDO':
                cursor.execute("""
                    UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
                    SET ID_ESTADO_CONSIGNADO = 9005,
                        CONSIGNADO = :consignado,
                        CONSIGNADO_OLD = :consignado_old,
                        NRO_DOC_IDENTIDAD = :nro_doc,
                        NRO_DOC_IDENTIDAD_OLD = :nro_doc_old,
                        TIPO_DOC_IDENTIDAD = :tipo_doc,
                        TIPO_DOC_IDENTIDAD_OLD = :tipo_doc_old
                    WHERE emision = :emision AND remito = :remito
                """, {'consignado': razonsocial, 'consignado_old': consignado, 'emision': emision, 'remito': remito, 'nro_doc': ruc, 'nro_doc_old': nro_doc, 'tipo_doc': 6, 'tipo_doc_old': tipo_doc})
                print(f"RUC {ruc} ACTIVO Y HABIDO.")
            else:
                obs = f"ESTADO: {estado}, CONDICIÓN: {condicion}"
                cursor.execute("""
                    UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
                    SET ID_ESTADO_CONSIGNADO = 9005,
                        ID_MOTIVO_CONSIGNADO = 9009,
                        OBS_VALIDACION_CONSIGNADO = :obs,
                        CONSIGNADO = :consignado,
                        CONSIGNADO_OLD = :consignado,
                        NRO_DOC_IDENTIDAD = :nro_doc,
                        NRO_DOC_IDENTIDAD_OLD = :nro_doc,
                        TIPO_DOC_IDENTIDAD = :tipo_doc,
                        TIPO_DOC_IDENTIDAD_OLD = :tipo_doc
                    WHERE emision = :emision AND remito = :remito
                """, {'obs': obs, 'consignado': consignado, 'emision': emision, 'remito': remito, 'nro_doc': nro_doc, 'tipo_doc': tipo_doc})
                print(f"RUC {ruc} NO ACTIVO O HABIDO.")
        else:
            obs = f"RUC NO EXISTE: {ruc}"
            handle_missing_ruc(cursor, ruc, tipo_doc, nro_doc, consignado, emision, remito, validate, obs)
    elif response.status_code == 204:
        obs = f"RUC NO EXISTE: {ruc}"
        handle_missing_ruc(cursor, ruc, tipo_doc, nro_doc, consignado, emision, remito, validate, obs)
    else:
        print(f"Error al consultar la API para el RUC {ruc}: {response.status_code}")

def handle_missing_ruc(cursor, ruc, tipo_doc, nro_doc, consignado, emision, remito, validate, obs):
    if validate:
        from validations.dni import handle_dni_validation
        handle_dni_validation(cursor, nro_doc, consignado, emision, remito)
    else:
        cursor.execute("""
            UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
            SET ID_ESTADO_CONSIGNADO = 9005,
                ID_MOTIVO_CONSIGNADO = 9010,
                OBS_VALIDACION_CONSIGNADO = :obs,
                CONSIGNADO = :consignado,
                CONSIGNADO_OLD = :consignado,
                NRO_DOC_IDENTIDAD = :nro_doc,
                NRO_DOC_IDENTIDAD_OLD = :nro_doc,
                TIPO_DOC_IDENTIDAD = :tipo_doc,
                TIPO_DOC_IDENTIDAD_OLD = :tipo_doc
            WHERE emision = :emision AND remito = :remito
        """, {'obs': obs, 'consignado': consignado, 'emision': emision, 'remito': remito, 'nro_doc': nro_doc, 'tipo_doc': tipo_doc})
        print(f"RUC NO ENCONTRADO PARA DNI {nro_doc}.")
