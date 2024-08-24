from validation import validate_dni
from validations.ruc10 import handle_ruc10_validation

def handle_dni_validation(cursor, nro_doc, tipo_doc, consignado, emision, remito, validate = True):
    result = validate_dni(nro_doc, consignado)
    if result["exists"] and validate == True:
        if result["match"]:
            ruc = f"10{nro_doc}{result['data']['digitoVerificador']}"
            consignado = result['full_name']
            handle_ruc10_validation(cursor, ruc, nro_doc, consignado, emision, remito, False)
        else:
            handle_no_match(cursor, nro_doc, result, emision, remito)
    else:
        handle_dni_not_found(cursor, nro_doc, emision, remito)

def handle_no_match(cursor, nro_doc, result, emision, remito):
    obs = f"NO MATCH DNI: {nro_doc} NOMBRE OBTENIDO: {result['full_name']}"
    cursor.execute("""
        UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
        SET ID_ESTADO_CONSIGNADO = 9006,
            ID_MOTIVO_CONSIGNADO = 9013,
            OBS_VALIDACION_CONSIGNADO = :obs
        WHERE emision= :emision AND remito = :remito
    """, {'obs': obs, 'emision': emision, 'remito': remito})
    print(f"DNI {nro_doc} VALIDO PERO NO COINCIDE. API Data: {result['data']}")

def handle_dni_not_found(cursor, nro_doc, emision, remito):
    obs = f"DNI {nro_doc}: NO EXISTE."
    cursor.execute("""
        UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
        SET ID_ESTADO_CONSIGNADO = 9006,
            ID_MOTIVO_CONSIGNADO = 9012,
            OBS_VALIDACION_CONSIGNADO = :obs
        WHERE emision= :emision AND remito = :remito
    """, {'obs': obs, 'emision': emision, 'remito': remito})
    print(f"DNI {nro_doc}: NO EXISTE.")