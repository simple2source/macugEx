import time
import psycopg2

#SELECT expire,pokemon_id, latitude, longitude FROM pokemon_map WHERE longitude > -74 AND longitude < -73 AND latitude > 40 AND latitude < 41 AND expire > 1476566012000 LIMIT 100
def get_pokemons_from_db(north, south, west, east):
    # 1. Open connection
    conn = psycopg2.connect(host = "week3demo1.cozbedhsxp0j.us-west-2.rds.amazonaws.com",
                            port = 5432,
                            user = "week3demo1",
                            password = "week3demo1",
                            database = "week3demo1")

    # 2. Execute SQL
    with conn.cursor() as cur:
        cur.execute("SELECT expire,pokemon_id, latitude, longitude" + 
                    " FROM pokemon_map " + 
                    " WHERE longitude > %s" +
                    " AND longitude < %s" +
                    " AND latitude > %s" +
                    " AND latitude < %s" +
                    " AND expire > %s" +
                    " LIMIT 100", 
                    (west, east, south, north, time.time() * 1000))
        rows = cur.fetchall()
        result = []
        for row in rows:
            # 1476566289000.0, 231, 41.4195807480884, -73.9995309631575)
            result.append({
                            "expire" : row[0],
                            "pokemon_id" : row[1],
                            "latitude" : row[2],
                            "longitude" : row[3]
                          })

    # 3. connection commit 
    conn.commit()
    return result
