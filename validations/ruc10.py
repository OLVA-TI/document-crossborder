def handle_ruc10_validation(cursor, ruc, tipo_doc, nro_doc, consignado, emision, remito, validate = True):
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
                    CONSIGNADO_OLD = :consignado_old,
                    NRO_DOC_IDENTIDAD = :nro_doc,
                    NRO_DOC_IDENTIDAD_OLD = :nro_doc_old,
                    TIPO_DOC_IDENTIDAD = :tipo_doc,
                    TIPO_DOC_IDENTIDAD_OLD = :tipo_doc_old
                WHERE emision= :emision AND remito = :remito
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
                WHERE emision= :emision AND remito = :remito
            """, {'obs': obs, 'consignado': consignado, 'emision': emision, 'remito': remito, 'nro_doc': nro_doc, 'tipo_doc': tipo_doc})
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
                    CONSIGNADO_OLD = :consignado,
                    NRO_DOC_IDENTIDAD = :nro_doc,
                    NRO_DOC_IDENTIDAD_OLD = :nro_doc,
                    TIPO_DOC_IDENTIDAD = :tipo_doc,
                    TIPO_DOC_IDENTIDAD_OLD = :tipo_doc
                WHERE emision= :emision AND remito = :remito
            """, {'obs': obs, 'consignado': consignado, 'emision': emision, 'remito': remito, 'nro_doc': nro_doc, 'tipo_doc': tipo_doc})
            print(f"RUC 10 NO ENCONTRADO PARA DNI {nro_doc}.")
