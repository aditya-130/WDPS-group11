
from candidate_generator import get_wikidata_entity_candidates
import spacy
import requests
import os
import sys

nlp = spacy.load('en_core_web_lg')

def disambiguate_entities(entities_list, weight=5):
    for ent_dict in entities_list:
        context_sentence = ent_dict["sentence"]  
        all_candidates = ent_dict.get("wikidata_candidates", [])
        best_candidate = None
        best_score = -1

        for candidate in all_candidates:
            description = candidate.get("description", "")
            altLabels = candidate.get("altLabels", [])
            popularity = candidate.get("popularity", 0)

            overlap_count = compute_overlap_score(context_sentence, description, altLabels)
            final_score = popularity + (overlap_count * weight)

            if final_score > best_score:
                best_score = final_score
                best_candidate = candidate

        ent_dict["best_candidate"] = best_candidate
        ent_dict["best_score"] = best_score

    return entities_list

def compute_overlap_score(context, description, alt_labels):    
    context_tokens = set(context.lower().split())
    desc_tokens = set(description.lower().split())
    alt_tokens = set()

    for lbl in alt_labels:
        alt_tokens.update(lbl.lower().split())

    candidate_tokens = desc_tokens.union(alt_tokens)
    overlap_count = len(context_tokens.intersection(candidate_tokens))
    return overlap_count

def extract_entities(text):
    doc = nlp(text)
    omit_labels = {"DATE", "TIME", "MONEY", "PERCENT", "CARDINAL"}
    entities_info = []

    for ent in doc.ents:
        if ent.label_ not in omit_labels:
            entity_dict = {
                "text": ent.text,
                "label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
                "sentence": ent.sent.text  
            }
            entities_info.append(entity_dict)

    return entities_info

def add_candidates(entities_list):
    for ent_dict in entities_list:
        entity_text = ent_dict["text"]
        wikidata_candidates = get_wikidata_entity_candidates(entity_text)        
        ent_dict["wikidata_candidates"] = wikidata_candidates
    
    return entities_list

def get_entities(question,answer):
    question_entities = extract_entities(question)
    question_entities = add_candidates(question_entities)
    disambiguated_questions = disambiguate_entities(question_entities, weight=5)

    entities = {'question_entities':[],'answer_entities':[]}

    for ent in disambiguated_questions:
        if (ent['best_candidate'] and ent['best_candidate']['article']):
            temp = [ent['text'],ent['best_candidate']['article'],ent['best_score']]
            entities['question_entities'].append(temp)

    answer_entities = extract_entities(answer)
    answer_entities = add_candidates(answer_entities)
    disambiguated_answers = disambiguate_entities(answer_entities, weight=5)

    for ent in disambiguated_answers:
        if (ent['best_candidate'] and ent['best_candidate']['article']):
            temp = [ent['text'],ent['best_candidate']['article'],ent['best_score']]
            entities['answer_entities'].append(temp)

    return entities