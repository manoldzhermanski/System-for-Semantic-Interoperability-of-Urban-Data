import requests

ORION_LD_URL = "http://localhost:1026"
ENTITY_TYPE = "GtfsStopTime"
CONTEXT_URL = "https://manoldzhermanski.github.io/System-for-Semantic-Interoperability-of-Urban-Data/gtfs-static/gtfs-static-context.jsonld"

HEADERS_GET = {
    "Accept": "application/ld+json",
    "Link": f'<{CONTEXT_URL}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}
HEADERS_DELETE = {
    "Accept": "application/json"
}

def get_entities_by_type(entity_type):
    url = f"{ORION_LD_URL}/ngsi-ld/v1/entities"
    params = {"type": entity_type, "limit": 1000}
    response = requests.get(url, headers=HEADERS_GET, params=params)
    response.raise_for_status()
    return response.json()

def delete_entity_by_id(entity_id):
    url = f"{ORION_LD_URL}/ngsi-ld/v1/entities/{entity_id}"
    response = requests.delete(url, headers=HEADERS_DELETE)
    return response.status_code == 204

def delete_all_entities_of_type(entity_type):
    entities = get_entities_by_type(entity_type)
    print(f"Намерени {len(entities)} обекта от тип {entity_type}")

    for entity in entities:
        entity_id = entity["id"]
        success = delete_entity_by_id(entity_id)
        if success:
            print(f"✅ Изтрито: {entity_id}")
        else:
            print(f"❌ Неуспех при изтриване: {entity_id}")

if __name__ == "__main__":
    for i in range(0, 180):
        print(f"Iteration {i + 1}")
        delete_all_entities_of_type(ENTITY_TYPE)
