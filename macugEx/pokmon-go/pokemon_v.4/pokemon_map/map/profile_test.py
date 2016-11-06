from views import *

def get_pokemon(north, south, west, east):
    # 2. Query database
    result = get_pokemons_from_db(north, south, west, east)

    # 3. Publish crawl job
    scan_area(float(north), float(south), float(west), float(east))

get_pokemon(41, 40, -74, -73)
