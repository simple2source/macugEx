import psycopg2

# INSERT INTO pokemon_map (encounter_id , expire , pokemon_id , latitude , longitude ) VALUES (1,1,1,1,1) ON CONFLICT (encounter_id) DO NOTHING;
def add_pokemon_to_db(encounter_id , expire , pokemon_id , latitude , longitude):
    # 1. Open connection
    conn = psycopg2.connect(host = "week2demo2.cozbedhsxp0j.us-west-2.rds.amazonaws.com",
                            port = 5432,
                            user = "week2demo2",
                            password = "week2demo2",
                            database = "week2demo2")

    # 2. Execute SQL
    with conn.cursor() as cur:
        cur.execute("INSERT INTO pokemon_map (encounter_id , expire , pokemon_id , latitude , longitude )" + 
                    " VALUES (%s, %s, %s, %s, %s)" + 
                    " ON CONFLICT (encounter_id) DO NOTHING", (encounter_id , expire , pokemon_id , latitude , longitude))

    # 3. connection commit 
    conn.commit()
    return
