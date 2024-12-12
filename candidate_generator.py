from SPARQLWrapper import SPARQLWrapper, JSON

def get_yago_entity_candidates(entity):
  
  sparql = SPARQLWrapper("http://yago-knowledge.org/sparql/query")
  sparql.setQuery(f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>

    SELECT ?entity (SAMPLE(?page) AS ?firstPage) WHERE {{
      ?entity rdfs:label "{entity}"@en .
      OPTIONAL {{ 
        ?entity schema:mainEntityOfPage ?page .
        FILTER(STRSTARTS(STR(?page), "https://en.wikipedia.org/wiki/"))
      }}
    }} GROUP BY ?entity
  """)
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()

  entities = []
  for result in results["results"]["bindings"]:
    entity_data = {
        "entity": result["entity"]["value"]
    }
    if "firstPage" in result:
      entity_data["firstPage"] = result["firstPage"]["value"]
    entities.append(entity_data)
  return entities

# Example usage with a parameter:
entity_to_search = "Athens"
entities_data = get_yago_entity_candidates(entity_to_search)

for entity_data in entities_data:
    print(entity_data, '\n')


def get_wikidata_entity_candidates(entity):

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(f"""
      SELECT ?entity ?article WHERE {{
        ?entity rdfs:label "{entity}"@en .
        OPTIONAL {{
          ?article schema:about ?entity ; 
                   schema:isPartOf <https://en.wikipedia.org/> .
        }}
      }}
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    entities = []
    for result in results["results"]["bindings"]:
        entity_data = {
            "entity": result["entity"]["value"]
        }
        if "article" in result:
            entity_data["article"] = result["article"]["value"]
        entities.append(entity_data)
    return entities

# Example usage with a parameter:
entity_to_search = "Athens"
entities_data = get_yago_entity_candidates(entity_to_search)

for entity_data in entities_data:
    print(entity_data, '\n')
    
entities_data = get_wikidata_entity_candidates(entity_to_search)

for entity_data in entities_data:
    print(entity_data, '\n')

