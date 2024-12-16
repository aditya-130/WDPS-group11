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


def get_wikidata_entity_candidates(entity):
    """
    Queries Wikidata for an entity string, returning a list of candidate dictionaries:
      - URI (entity)
      - Wikipedia article link (article)
      - textual description (description)
      - synonyms (altLabels)
      - popularity (sitelinkCount)
    """
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(f"""
    PREFIX schema: <http://schema.org/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX wikibase: <http://wikiba.se/ontology#>

    SELECT ?entity ?article ?description (GROUP_CONCAT(DISTINCT ?altLabel; separator="|") AS ?allAltLabels) ?sitelinkCount
    WHERE {{
      ?entity rdfs:label "{entity}"@en .
      
      OPTIONAL {{
        ?article schema:about ?entity ;
                 schema:isPartOf <https://en.wikipedia.org/> .
      }}

      OPTIONAL {{
        ?entity schema:description ?description .
        FILTER(LANG(?description) = "en")
      }}

      OPTIONAL {{
        ?entity skos:altLabel ?altLabel .
        FILTER(LANG(?altLabel) = "en")
      }}

      OPTIONAL {{
        ?entity wikibase:sitelinks ?sitelinkCount .
      }}
    }}
    GROUP BY ?entity ?article ?description ?sitelinkCount
    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    entities = []
    for result in results["results"]["bindings"]:
        entity_data = {
            "entity": result["entity"]["value"],      # Wikidata URI
            "article": result.get("article", {}).get("value", None),
            "description": result.get("description", {}).get("value", ""),
            "altLabels": [],
            "popularity": 0  # default
        }

        # Parse altLabels
        if "allAltLabels" in result and "value" in result["allAltLabels"]:
            alt_labels_str = result["allAltLabels"]["value"]
            if alt_labels_str:
                entity_data["altLabels"] = alt_labels_str.split("|")

        # Parse sitelinks (popularity)
        if "sitelinkCount" in result and "value" in result["sitelinkCount"]:
            # It's typically a string like "283" which we can convert to int
            entity_data["popularity"] = int(result["sitelinkCount"]["value"])

        entities.append(entity_data)

    return entities