import requests
import os
from dotenv import load_dotenv
load_dotenv(override=True)
from validation import compare_names

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
                            CONSIGNADO_OLD = CONSIGNADO,
                            CONSIGNADO = :consignado,
                            NRO_DOC_IDENTIDAD_OLD = NRO_DOC_IDENTIDAD,
                            NRO_DOC_IDENTIDAD = :nro_doc,
                            TIPO_DOC_IDENTIDAD_OLD = TIPO_DOC_IDENTIDAD,
                            TIPO_DOC_IDENTIDAD = :tipo_doc
                        WHERE emision = :emision AND remito = :remito
                    """, {'consignado': razonsocial, 'emision': emision, 'remito': remito, 'nro_doc': ruc, 'tipo_doc': tipo_doc})
                    print(f"RUC {ruc} ACTIVO Y HABIDO.")
                else:
                    obs = f"ESTADO: {estado}, CONDICIÓN: {condicion}"
                    cursor.execute("""
                        UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
                        SET ID_ESTADO_CONSIGNADO = 9006,
                            ID_MOTIVO_CONSIGNADO = 9009,
                            OBS_VALIDACION_CONSIGNADO = :obs,
                            CONSIGNADO_OLD = CONSIGNADO,
                            CONSIGNADO = :consignado,
                            NRO_DOC_IDENTIDAD_OLD = NRO_DOC_IDENTIDAD,
                            NRO_DOC_IDENTIDAD = :nro_doc,
                            TIPO_DOC_IDENTIDAD_OLD = TIPO_DOC_IDENTIDAD,
                            TIPO_DOC_IDENTIDAD = :tipo_doc
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

