import unidecode

def handle_ruc20_validation(cursor, ruc, consignado, emision, remito):
    cursor.execute("""
        SELECT RAZONSOCIAL, ESTADOCONTRIBUYENTE, CONDICIONDOMICILIO
        FROM OLVA_CORP.CONTRIBUYENTE
        WHERE RUC = :ruc
    """, {'ruc': ruc})
    contribuyente = cursor.fetchone()
    if contribuyente:
        razonsocial, estado, condicion = contribuyente
        match = compare_names(razonsocial, consignado)
        if match == True:
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
                    SET ID_ESTADO_CONSIGNADO = 9006,
                        ID_MOTIVO_CONSIGNADO = 9009,
                        OBS_VALIDACION_CONSIGNADO = :obs,
                        CONSIGNADO = :consignado,
                        RUC = :ruc
                    WHERE emision= :emision AND remito = :remito
                """, {'obs': obs, 'consignado': consignado, 'emision': emision, 'remito': remito, 'ruc': ruc})
                print(f"RUC {ruc} NO ACTIVO O HABIDO.")
        else:
            obs = f"RUC NO MATCH: {ruc} RAZON SOCIAL: {razonsocial}"
            cursor.execute("""
                UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
                SET ID_ESTADO_CONSIGNADO = 9006,
                    ID_MOTIVO_CONSIGNADO = 9011,
                    OBS_VALIDACION_CONSIGNADO = :obs
                WHERE emision= :emision AND remito = :remito
            """, {'obs': obs, 'emision': emision, 'remito': remito})
            print(f"RUC {ruc} NO MATCH.")
    else:
        obs = f"RUC NO EXISTE: {ruc}"
        cursor.execute("""
            UPDATE olvadesa.TBL_CLIENTE_INTERNACIONAL
            SET ID_ESTADO_CONSIGNADO = 9006,
                ID_MOTIVO_CONSIGNADO = 9010,
                OBS_VALIDACION_CONSIGNADO = :obs
            WHERE emision= :emision AND remito = :remito
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