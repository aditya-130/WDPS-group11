# Dependencies
# !pip install sparqlwrapper
# !python -m spacy download en_core_web_md


from SPARQLWrapper import SPARQLWrapper, JSON
import spacy
import re
#nlp = spacy.load("en_core_web_sm")
nlp = spacy.load("en_core_web_md")

from sentence_transformers import SentenceTransformer, util

import gensim.downloader as api
from numpy import dot
from numpy.linalg import norm
import requests

# Load pretrained Word2Vec model
word2vecModel = api.load("glove-wiki-gigaword-100")
# Load Sentence Transformer Model
sentenceTransformerModel = SentenceTransformer('all-MiniLM-L6-v2')

def polarToDeclarative(text): #Handles do- questions unintendedly
  #Uses the fact that polar questions in english are often created through a subject-auxiliary inversion
  #At a very basic level, that means that we can put the auxiliary verb after the subject to turn it into a declaration
  #To make it more robust, we could construct a syntax tree and put the auxiliary in the right place,
  #(rant) but spacy doesn't seem to make syntax trees like a linguistics textbook so I have absolutely no idea if that is even possible
  doc = nlp(text)
  subject = None
  auxilliary = None
  other = []
  for token in doc:
    if token.dep_ == "nsubj":
      subject = token.text
    elif token.dep_ == "aux" or token.dep_ == "ROOT": #It is possible that the verb is inverted
      auxilliary = token.text
    else:
      other.append(token) #Put other words in order
  if subject and auxilliary:
    print(auxilliary)
    declarative = f"{subject.capitalize()} {auxilliary.lower()} " + " ".join([token.text for token in other])
    print(declarative)
    return declarative.rstrip("?")

def contentReplacer(entity, question):
  result = question
  print(result)
  result = re.sub(r'\b(who|what|when|where|why)\b', entity, question, flags=re.IGNORECASE)
  print(result)
  print("RETURN")
  return result

def relationTriplets(doc):
  triplets = []  # To store all valid triplets

  for token in doc:
    if token.dep_ == "ROOT":  # Main verb of the sentence
      sbjs = [subjects for subjects in token.lefts if subjects.dep_ == "nsubj"]  # Subject(s)
      objs = [objects for objects in token.rights if objects.dep_ in ("dobj", "attr", "pobj")]  # Object(s)
      rel = token.text  # Predicate (verb)

      # Process subjects and objects for named entities or compound phrases
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

def noMoreCamels(camel): #camelCase is not well processed
  return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', camel).lower()

def URLtoText(url):
  if ("#" in url):
    val = url.split("#")[-1].replace("_", " ")
  else:
    val = url.split("/")[-1].replace("#", " ").replace("_", " ")
  return noMoreCamels(val)


def similarity(phrase1, phrase2):
  doc1 = nlp(phrase1)
  doc2 = nlp(phrase2)
  return doc1.similarity(doc2)

def relBetweenTwo(sbj, obj):
  # SPARQL query to get all triples where the entity is the subject or object
  # Works both ways
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
  sparql_endpoint = "https://yago-knowledge.org/sparql/query"
  sparql = SPARQLWrapper(sparql_endpoint)
  sparql.setQuery(query)
  sparql.setReturnFormat(JSON)

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


def isCamelCase(string):
  return bool(re.match(r'^[a-z]+([A-Z][a-z]*)*$', string))

def yagoToDBPedia(yago_url):
  #So DBPedia has a more detailed abstract, Yago has a very very very simple one. Therefore as a last resort, we move do DBPedia to compare facts
  dbpedia_url = yago_url.replace("yago-knowledge.org/resource", "dbpedia.org/page")
  response = requests.get(dbpedia_url)
  if response.status_code == 200:
    return dbpedia_url
  else:
    return None

def get_dbpedia_abstract(entity):
  sparql = SPARQLWrapper("http://dbpedia.org/sparql")
  sparql.setQuery(f"""
      PREFIX dbo: <http://dbpedia.org/ontology/>
      SELECT ?abstract
      WHERE {{
        <{entity}> dbo:abstract ?abstract .
        FILTER (lang(?abstract) = 'en')
      }}
  """)
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()

  for result in results["results"]["bindings"]:
    return result["abstract"]["value"]
  return None

def checkQuery(sbj, obj, text): #Query vs Relation sentence-level matching
  rels = relBetweenTwo(sbj,obj)
  if not rels:
    return None
  for rel in rels:
    tempTriplet = URLtoText(sbj), URLtoText(rel), URLtoText(obj)
    #print(tripletsToSentence(tempTriplet))
    if betterSim(text, tripletsToSentence(tempTriplet)) > 0.90:
      return "correct"
  else:
    return "incorrect"

def checkSynonyms(sbj, obj, extractedRelation): #Relation vs Relation word-level matching
  rels = relBetweenTwo(sbj, obj)
  for rel in rels:
    st = URLtoText(rel)
    words = [st]
    if isCamelCase(st):
      words = noMoreCamels(st).split()
      #print(words)
    for word in words:
      #print(f"Comparing {lemmatise(extractedRelation)} and {lemmatise(word)}")
      if synonyms(lemmatise(extractedRelation), lemmatise(word)):
        #print(f"{extractedRelation} and {word} are synonyms")
        return True
  return False

def compareAbstract(sbj, obj, text): #Sentence to Paragraph level matching
  sbj = yagoToDBPedia(sbj)
  obj = yagoToDBPedia(obj)
  if sbj and obj:
    sbjAbstract = get_dbpedia_abstract(sbj)
    objAbstract = get_dbpedia_abstract(obj)
  else:
    return None
  if betterSim(text, sbjAbstract) > 0.90:
    return "correct"
  if betterSim(text, objAbstract) > 0.90:
    return "correct"
  else:
    return "incorrect"

def betterSim(sentence1, sentence2): #Sentence level similarity
  embedding1 = sentenceTransformerModel.encode(sentence1, convert_to_tensor=True)
  embedding2 = sentenceTransformerModel.encode(sentence2, convert_to_tensor=True)
  #print(util.cos_sim(embedding1, embedding2))
  return util.cos_sim(embedding1, embedding2)

def cosine_similarity(vec1, vec2):
  return dot(vec1, vec2) / (norm(vec1) * norm(vec2))

def synonyms(word1, word2):
  vector1 = word2vecModel[word1]
  vector2 = word2vecModel[word2]
  similarity = cosine_similarity(vector1, vector2)
  threshold = 0.5
  #print(similarity)
  if similarity >= threshold:
    return True
  else:
    return False

def extractRelation(sentence):
  doc = nlp(sentence)
  entities = [ent.text for ent in doc.ents]
  relation = None

  # Find relations based on dependency
  for token in doc:
    # Word Order
    if token.dep_ == 'nsubj' and token.head.pos_ == 'VERB':
    # Predicate (verb) is often the relation
      relation = token.head.lemma_  # Since we do word level matching, use lemmatisation to simplify
      break
    elif token.dep_ == 'attr' and token.pos_ == 'NOUN':
      # Nouns can also be a relation (Ankara is the "capital" of Turkey)
      relation = token.text
      break
    elif token.dep_ == 'prep' and token.head.pos_ == 'VERB':
      # Prepositions are also a candidate (Monas is "in" Jakarta)
      relation = token.text
      break

  return relation


def lemmatise(word):
  doc = nlp(word)
  return doc[0].lemma_


def factCheckPipeline(sbj, obj, text):
  if extractRelation(text): #Determine if the relation is parsable
    if checkSynonyms(sbj, obj, extractRelation(text)): #If possible, and exists a relation between the two objects, then check if synonym
      print("correct")
      return True
    else:
      print("incorrect")
      return False
  else: #If relation cannot be parsed, then just check similarity between queries
    t2 = checkQuery(sbj, obj, text) #Restructures query and relation, then compares similarity between two sentences

    if t2: #Can return None, when middle fails
      if t2 == "correct":
        print("correct")
        return True
      else:
        print("incorrect")
        return False
  #If we arrive here, the relation cannot be parsed with our functions
  #and the relationship does not exist in graph (incomplete knowledge)
  #Therefore we just compare the query to the wikipedia page
  t3 = compareAbstract(sbj, obj, text)
  if t3:
    if t3 == "correct":
      print("correct")
      return True
    else:
      print("incorrect")
      return False
  else:
    print("incorrect")
    return False

#TEST 1

text = "Seoul is the capital of South Korea"
sbj = "http://yago-knowledge.org/resource/Seoul"
obj = "http://yago-knowledge.org/resource/South_Korea"


a = factCheckPipeline(sbj, obj, text)

text = "Busan is the capital of South Korea"
sbj = "http://yago-knowledge.org/resource/Busan"
obj = "http://yago-knowledge.org/resource/South_Korea"


a = factCheckPipeline(sbj, obj, text)

#TEST 2

text = "Shakespeare wrote Romeo and Juliet"
sbj = "http://yago-knowledge.org/resource/William_Shakespeare"
obj = "http://yago-knowledge.org/resource/Romeo_and_Juliet"

a = factCheckPipeline(sbj, obj, text)

text = "Shakespeare wrote War and Peace"
sbj = "http://yago-knowledge.org/resource/William_Shakespeare"
obj = "http://yago-knowledge.org/resource/War_and_Peace"

a = factCheckPipeline(sbj, obj, text)

text = "Tolstoy wrote Romeo and Juliet"
sbj = "http://yago-knowledge.org/resource/Leo_Tolstoy"
obj = "http://yago-knowledge.org/resource/Romeo_and_Juliet"

a = factCheckPipeline(sbj, obj, text)

#TEST 3

text = "Joe Biden is President of the United States"
sbj = "http://yago-knowledge.org/resource/Joe_Biden"
obj = "http://yago-knowledge.org/resource/United_States"

a = factCheckPipeline(sbj, obj, text)

text = "Elon Musk is President of the United States"
sbj = "http://yago-knowledge.org/resource/Joe_Biden"
obj = "http://yago-knowledge.org/resource/United_States"

a = factCheckPipeline(sbj, obj, text)
