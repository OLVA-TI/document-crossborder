def handle_ruc10_validation(cursor, ruc, nro_doc, consignado, emision, remito, validate = True):
    cursor.execute("""
        SELECT RAZONSOCIAL, ESTADOCONTRIBUYENTE, CONDICIONDOMICILIO
        FROM CONTRIBUYENTE
        WHERE RUC = :ruc
    """, {'ruc': ruc})
    contribuyente = cursor.fetchone()
    if contribuyente:
        razonsocial, estado, condicion = contribuyente
        if estado == 'ACTIVO' and condicion == 'HABIDO':
            cursor.execute("""
                UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
                SET ID_ESTADO_CONSIGNADO = 9005,
                    CONSIGNADO = :consignado,
                    RUC = :ruc
                WHERE emision= :emision AND remito = :remito
            """, {'consignado': razonsocial, 'emision': emision, 'remito': remito, 'ruc': ruc})
            print(f"RUC {ruc} ACTIVO Y HABIDO.")
        else:
            obs = f"ESTADO: {estado}, CONDICIÓN: {condicion}"
            cursor.execute("""
                UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
                SET ID_ESTADO_CONSIGNADO = 9005,
                    ID_MOTIVO_CONSIGNADO = 9009,
                    OBS_VALIDACION_CONSIGNADO = :obs,
                    CONSIGNADO = :consignado,
                    DNI = :dni
                WHERE emision= :emision AND remito = :remito
            """, {'obs': obs, 'consignado': consignado, 'emision': emision, 'remito': remito, 'dni': nro_doc})
            print(f"RUC {ruc} NO ACTIVO O HABIDO.")
    else:
        obs = f"RUC NO EXISTE: {ruc}"
        if (validate == True):
            from validations.dni import handle_dni_validation
            handle_dni_validation(cursor, nro_doc, consignado, emision, remito)
        else:
            cursor.execute("""
                UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
                SET ID_ESTADO_CONSIGNADO = 9005,
                    ID_MOTIVO_CONSIGNADO = 9010,
                    OBS_VALIDACION_CONSIGNADO = :obs,
                    CONSIGNADO = :consignado,
                    DNI = :dni
                WHERE emision= :emision AND remito = :remito
            """, {'obs': obs, 'consignado': consignado, 'emision': emision, 'remito': remito, 'dni': nro_doc})
            print(f"RUC 10 NO ENCONTRADO PARA DNI {nro_doc}.")
