#We might need en_core_web_md for the next part, because of semantic distance and whatnot
#TO DO: if no relation found, then compare the relation triplet to the wikipedia or yago entry

from SPARQLWrapper import SPARQLWrapper, JSON
from sentence_transformers import SentenceTransformer, util
import spacy
import re
#nlp = spacy.load("en_core_web_sm")
nlp = spacy.load("en_core_web_md")

def polarToDeclarative(doc):
  #Implement that later
  return sentence

def contentReplacer(entity, question):
  result = question
  print(result)
  result = re.sub(r'\b(who|what|when|where|why)\b', entity, question, flags=re.IGNORECASE)
  print(result)
  print("RETURN")
  return result

def relationTriplets(doc):
    triplets = []

    for token in doc:
        if token.dep_ == "ROOT":  # Predicate
            sbjs = [subjects for subjects in token.lefts if subjects.dep_ == "nsubj"]  # Subject
            objs = [objects for objects in token.rights if objects.dep_ in ("dobj", "attr", "pobj")]  # Object
            rel = token.text  # Predicate

            subject_entities = []
            object_entities = []
            for sub in sbjs:
                compound_sub = " ".join(
                    [child.text for child in sub.subtree]
                )  # Include all tokens in the subject's subtree
                subject_entities.append(compound_sub)
            for obj in objs:
                # If the object is part of a compound phrase (e.g., "Romeo and Juliet"), capture it
                compound_obj = " ".join(
                    [child.text for child in obj.subtree]
                )  # Include all tokens in the object's subtree
                object_entities.append(compound_obj)
            #print(subject_entities)
            #print(object_entities)
            # Create triplets
            for sbj_entity in subject_entities:
              for obj_entity in object_entities:
                 triplets.append((sbj_entity, rel, obj_entity))

    if not triplets:
        print("NO RELATION FOUND")
        return None
    save = []
    for entry in range(len(triplets[0])):
      #print(triplets[0][entry])
      save.append(re.sub(r'^(a|an|the)\s+', '', triplets[0][entry], flags=re.IGNORECASE))
    return (save[0], save[1], save[2])
    #return triplets

def tripletsToSentence(triplets):
  return " ".join(triplets)

def noMoreCamels(camel):
  return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', camel).lower()

def URLtoText(url):
  if ("#" in url):
    val = url.split("#")[-1].replace("_", " ")
  else:
    val = url.split("/")[-1].replace("#", " ").replace("_", " ")
  return noMoreCamels(val)

#print(predicateURLtoText("http://schema.org/alternateName"))  # Output: "Alternate name"

def similarity(phrase1, phrase2):
  doc1 = nlp(phrase1)
  doc2 = nlp(phrase2)
  return doc1.similarity(doc2)

def relBetweenTwo(sbj, obj):
    # SPARQL query to get all triples where the entity is the subject or object
    query = f"""
    PREFIX yago: <http://yago-knowledge.org/resource/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    """

    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?property ?value
    WHERE {{
      {{
        <{sbj}> ?property <{obj}> .
      }} UNION {{
        <{obj}> ?property <{sbj}> .
      }}
    }}
    """
    # YAGO SPARQL endpoint
    sparql_endpoint = "https://yago-knowledge.org/sparql/query"

    # Query the SPARQL endpoint
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)


    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    # Execute the query and process results
    results = sparql.query().convert()

    # Output results
    #print(f"Relationships between {URLtoText(sbj).capitalize()} and {URLtoText(obj).capitalize()}:")
    returnRes = []
    for result in results["results"]["bindings"]:
        #print(f"Property: {result['property']['value']}")
        returnRes.append(result['property']['value'])
    return returnRes


    for result in results["results"]["bindings"]:
        relString = f"{URLtoText(sbj)} {URLtoText(result['property']['value'])} {URLtoText(obj)}"
        print("QUERY IS: ", queryString)
        print("RELATION IS: ", relString)
        print(similarity(relString, queryString))

#With Spacy
def check(sbj, obj, doc):
  queryTriplet = relationTriplets(doc)
  rels = relBetweenTwo(sbj, obj, queryTriplet)
  for rel in rels:
    print(tripletsToSentence(queryTriplet))
    tempTriplet = URLtoText(sbj), URLtoText(rel), URLtoText(obj)
    print(tripletsToSentence(tempTriplet))
    print(similarity(tripletsToSentence(queryTriplet).lower(), tripletsToSentence(tempTriplet).lower()))

#With Sentence Transformer
def checkQuery(sbj, obj, text):
  rels = relBetweenTwo(sbj,obj)
  for rel in rels:
    tempTriplet = URLtoText(sbj), URLtoText(rel), URLtoText(obj)
    print(tripletsToSentence(tempTriplet))
    print(betterSim(text, tripletsToSentence(tempTriplet)))

#With Sentence Transformer
def betterSim(sentence1, sentence2):
  embedding1 = model.encode(sentence1, convert_to_tensor=True)
  embedding2 = model.encode(sentence2, convert_to_tensor=True)
  return util.cos_sim(embedding1, embedding2)

#Import Sentence Transformer NLP thing
model = SentenceTransformer('all-MiniLM-L6-v2')

#TEST 1

text = "Seoul is the capital of South Korea"
doc = nlp(text)

sbj = "http://yago-knowledge.org/resource/Seoul"
obj = "http://yago-knowledge.org/resource/South_Korea"

checkQuery(sbj, obj, text)

#TEST 2

text = "Shakespeare wrote Romeo and Juliet"
doc = nlp(text)

sbj = "http://yago-knowledge.org/resource/William_Shakespeare"
obj = "http://yago-knowledge.org/resource/Romeo_and_Juliet"

checkQuery(sbj, obj, text)

#TEST 3

text = "Joe Biden is President of the United States"
doc = nlp(text)

sbj = "http://yago-knowledge.org/resource/Joe_Biden"
obj = "http://yago-knowledge.org/resource/President_of_the_United_States"

check(sbj, obj, text)