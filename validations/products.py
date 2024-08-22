from unidecode import unidecode
from fuzzywuzzy import fuzz

def handle_products_validation(cursor, emision, remito):
    cursor.execute("""
    SELECT
        x.DESCRIPCION
    FROM
        OLVADESA.TBL_CLIENTE_INTERNACIONAL_DET x
    WHERE
        x.EMISION = :emision
        AND x.REMITO = :remito
    """, {'emision': emision, 'remito': remito})
    rows = cursor.fetchall()

    cursor.execute("""
    SELECT
        x.DESCRIPCION
    FROM
        OLVA_CORP.PRODUCTO_RESTRINGIDO_PERSONA x
    """)
    restricted = cursor.fetchall()

    restricted_products = [unidecode(item[0].lower()) for item in restricted]

    # Umbral de similitud
    similarity_threshold = 60

    for row in rows:
        descripcion = unidecode(row[0].lower())
        for restricted_item in restricted_products:
            similarity = fuzz.partial_ratio(restricted_item, descripcion)
            print(similarity, similarity_threshold, descripcion, restricted_item)
            if similarity >= similarity_threshold:
                cursor.execute("""
                UPDATE OLVADESA.TBL_CLIENTE_INTERNACIONAL
                SET POSIBLE_RESTRINGIDO = 1
                WHERE EMISION = :emision
                    AND REMITO = :remito
                """, {'emision': emision, 'remito': remito})
                return