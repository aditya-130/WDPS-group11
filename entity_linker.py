
from candidate_generator import get_yago_entity_candidates, get_wikidata_entity_candidates
import spacy
import requests
import os
import sys

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
    

# def search_wikipedia(entity_name, entity_label):
    
#     label_to_search_term = {
#         "ORG": f"{entity_name} (company)",  
#         "PRODUCT": f"{entity_name} (product)",
#         "PERSON": f"{entity_name} (person)",  
#         "GPE": f"{entity_name} (place)",
#         "FAC": f"{entity_name} (building)",
#         "LOC": f"{entity_name} (location)", 
#         "DATE": f"{entity_name} (date)", 
#         "TIME": f"{entity_name} (time)",  
#         "MONEY": f"{entity_name} (money)",  
#         "PERCENT": f"{entity_name} (percent)" 
#     }

qa_dict = {
    "What is the capital of Turkey": "The capital of Turkey is Ankara. It became the capital in 1923, replacing Istanbul (formerly Constantinople) as the center of government.",
    "Who founded the company Apple": "Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.",
    "Is Managua the capital of Nicaragua?": "Yes, Managua is the capital city of Nicaragua.",
    "What year was Vrije University Amsterdam established": "Vrije University Amsterdam was established in 1880.",
    "Which person betrayed Caesar": "Julius Caesar was betrayed by Brutus, among others.",
    "What are some fauna that live in the 'Amazon Rainforest'": "The Amazon rainforest is home to many species including jaguars, sloths, macaws, and poison dart frogs.",
    "Who invented the telephone?": "The telephone was invented by Alexander Graham Bell in 1876.",
    "What is the largest ocean on Earth?": "The Pacific Ocean is the largest ocean on Earth, covering more than 63 million square miles.",
    "When did the Titanic sink?": "The Titanic sank on April 15, 1912, after hitting an iceberg in the North Atlantic.",
    "What is the tallest mountain in the world?": "Mount Everest is the tallest mountain in the world, standing at 8,848.86 meters (29,031.7 feet).",
    "Who wrote the play 'Romeo and Juliet'?": "The play 'Romeo and Juliet' was written by William Shakespeare in the early stages of his career."
}

qa_list = list(qa_dict.items())
index = 1
if 0 <= index < len(qa_list):
    question, answer = qa_list[index]
    print(f"Question: {question}")
    print(f"Answer: {answer}")
else:
    print("Invalid index")

#from llama_cpp import Llama
# sys.stderr = open(os.devnull, 'w') # prevents printing warnings like "llama_new_context_with_model: n_ctx_per_seq (512) < n_ctx_train (4096) -- the full capacity of the model will not be utilized"

# model_path = "models/llama-2-7b.Q4_K_M.gguf"

# question = input('\033[1m' + "Input (A): " + '\033[0m')
# llm = Llama(model_path=model_path, verbose=False)
# output = llm(
#       question, # Prompt
#       max_tokens=128
#       # stop = ['Q:', '?']
#       # stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
#       # echo=True # Echo the prompt back in the output
# )
# answer = output['choices'][0]['text']

# print('\033[1m' + "\nText returned by the language model (B) (llama 2, 70B):"  + '\033[0m', answer, '\n') 


nlp = spacy.load('en_core_web_lg')

question_entities = extract_entities(question)
question_entities = add_candidates(question_entities)
disambiguated_questions = disambiguate_entities(question_entities, weight=5)
print("\n Linked Entities in the question: ")
for ent in disambiguated_questions:
    print(f"\nEntity: {ent['text']}")
    print(f"Best Score: {ent['best_score']}")
    print("Best Candidate:", ent["best_candidate"]["entity"])
    print("Description:", ent["best_candidate"]["description"])

answer_entities = extract_entities(answer)
answer_entities = add_candidates(answer_entities)
disambiguated_answers = disambiguate_entities(answer_entities, weight=5)
print("\n Linked Entities in the answer: ")
for ent in disambiguated_answers:
    print(f"\nEntity: {ent['text']}")
    print(f"Best Score: {ent['best_score']}")
    print("Best Candidate:", ent["best_candidate"]["entity"])
    print("Description:", ent["best_candidate"]["description"])




