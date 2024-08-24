from database import get_connection
from validations.dni import handle_dni_validation
from validations.ruc10 import handle_ruc10_validation
from validations.ruc20 import handle_ruc20_validation
from validations.products import handle_products_validation
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                process_records(cursor)
            connection.commit()
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        print(f"An unexpected error occurred: {str(e)}")

def process_records(cursor):
    cursor.execute("""
    SELECT
        tb.TIPO_DOC_IDENTIDAD,
        REPLACE(tb.NRO_DOC_IDENTIDAD, CHR(160), '') NRO_DOC_IDENTIDAD,
        tb.CONSIGNADO,
        tb.EMISION,
        tb.REMITO
    FROM
        olvadesa.TBL_CLIENTE_INTERNACIONAL tb
    INNER JOIN OLVA_CORP.PAQUETE_DECLARADO pd ON
        pd.ID = tb.id_paquete_declarado
    WHERE
        tb.id_estado_consignado = 9004
    """)
    rows = cursor.fetchall()
    for row in rows:
        process_row(cursor, row)

def process_row(cursor, row):
    tipo_doc, nro_doc, consignado, emision, remito = row
    handle_products_validation(cursor, emision, remito)

    if int(tipo_doc) == 1:
        handle_dni_validation(cursor, nro_doc, tipo_doc, consignado, emision, remito)
    elif int(tipo_doc) == 6 and nro_doc.startswith('10'):
        ruc = nro_doc
        nro_doc = ruc[2:-1]
        handle_ruc10_validation(cursor, ruc, nro_doc, tipo_doc, consignado, emision, remito)
    elif int(tipo_doc) == 6:#and (nro_doc.startswith('20') or nro_doc.startswith('15'))
        ruc = nro_doc
        nro_doc = ruc[2:-1]
        handle_ruc20_validation(cursor, ruc, tipo_doc, consignado, emision, remito)
    

if __name__ == "__main__":
    main()
