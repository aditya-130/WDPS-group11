<<<<<<< HEAD
<<<<<<< HEAD
from llama_cpp import Llama
import spacy
import requests
import os
import sys

def search_wikipedia(entity_name, entity_label):
    search_url = f"https://en.wikipedia.org/w/api.php"
    entity_name = entity_name.replace(" ", "_")
=======
=======
from llama_cpp import Llama
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)
import spacy
import requests
import os
import sys

def search_wikipedia(entity_name, entity_label):
    search_url = f"https://en.wikipedia.org/w/api.php"
    entity_name = entity_name.replace(" ", "_")
<<<<<<< HEAD

>>>>>>> 2db3c16 (entity linker)
=======
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)
    label_to_search_term = {
        "ORG": f"{entity_name} (company)",  
        "PRODUCT": f"{entity_name} (product)",
        "PERSON": f"{entity_name} (person)",  
        "GPE": f"{entity_name} (place)",
        "FAC": f"{entity_name} (building)",
        "LOC": f"{entity_name} (location)", 
        "DATE": f"{entity_name} (date)", 
        "TIME": f"{entity_name} (time)",  
        "MONEY": f"{entity_name} (money)",  
        "PERCENT": f"{entity_name} (percent)" 
    }
    
    search_term = label_to_search_term.get(entity_label, entity_name)
    
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': search_term,
        'format': 'json',
        'utf8': 1
    }
<<<<<<< HEAD
<<<<<<< HEAD
=======

>>>>>>> 2db3c16 (entity linker)
=======
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)
    response = requests.get(search_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        search_results = data['query']['search']
        
        if search_results:
            top_result_title = search_results[0]['title']
            return f"https://en.wikipedia.org/wiki/{top_result_title.replace(' ', '_')}"
    
    return None
<<<<<<< HEAD
<<<<<<< HEAD
def link_entities_to_wikipedia(text):
    doc = nlp(text)
    entity_links = {}
    omit_labels = {"DATE", "TIME", "MONEY", "PERCENT", "CARDINAL"}
=======

=======
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)
def link_entities_to_wikipedia(text):
    doc = nlp(text)
    entity_links = {}
<<<<<<< HEAD
    omit_labels = {"DATE", "TIME", "MONEY", "PERCENT"}

>>>>>>> 2db3c16 (entity linker)
=======
    omit_labels = {"DATE", "TIME", "MONEY", "PERCENT", "CARDINAL"}
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)
    for ent in doc.ents:
        entity_name = ent.text
        entity_label = ent.label_
        
        if entity_label in omit_labels:
            continue
        
<<<<<<< HEAD
<<<<<<< HEAD
        # print(f"{entity_name}: {entity_label}")
        link = search_wikipedia(entity_name, entity_label)
        if link:
            entity_links[ent.text] = link
    return entity_links


"""
=======
        print(f"{entity_name}: {entity_label}")
=======
        # print(f"{entity_name}: {entity_label}")
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)
        link = search_wikipedia(entity_name, entity_label)
        if link:
            entity_links[ent.text] = link
    return entity_links


<<<<<<< HEAD
>>>>>>> 2db3c16 (entity linker)
=======
"""
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)
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
<<<<<<< HEAD
<<<<<<< HEAD
=======

>>>>>>> 2db3c16 (entity linker)
=======
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)
qa_list = list(qa_dict.items())
index = 5
if 0 <= index < len(qa_list):
    question, answer = qa_list[index]
    print(f"Question: {question}")
    print(f"Answer: {answer}")
else:
    print("Invalid index")
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)
"""

sys.stderr = open(os.devnull, 'w') # prevents printing warnings like "llama_new_context_with_model: n_ctx_per_seq (512) < n_ctx_train (4096) -- the full capacity of the model will not be utilized"

model_path = "models/llama-2-7b.Q4_K_M.gguf"

question = input('\033[1m' + "Input (A): " + '\033[0m')
llm = Llama(model_path=model_path, verbose=False)
output = llm(
      question, # Prompt
      max_tokens=128
      # stop = ['Q:', '?']
      # stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
      # echo=True # Echo the prompt back in the output
)
answer = output['choices'][0]['text']

print('\033[1m' + "\nText returned by the language model (B) (llama 2, 70B):"  + '\033[0m', answer, '\n') 



<<<<<<< HEAD
=======
>>>>>>> 2db3c16 (entity linker)
=======
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)

nlp = spacy.load('en_core_web_lg')
answer_entity_links = link_entities_to_wikipedia(answer)
question_entity_links = link_entities_to_wikipedia(question)

<<<<<<< HEAD
<<<<<<< HEAD
print('\033[1m' + "Entities extracted:\n" + '\033[0m')
# print("\nLinked Entities in the Answer:")
for entity, link in answer_entity_links.items():
    print(f"{entity}: {link}")
# print("\nLinked Entities in the Question:")
for entity, link in question_entity_links.items():
    print(f"{entity}: {link}")
=======
print("\nLinked Entities in the Answer:")
=======
print('\033[1m' + "Entities extracted:\n" + '\033[0m')
# print("\nLinked Entities in the Answer:")
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)
for entity, link in answer_entity_links.items():
    print(f"{entity}: {link}")
# print("\nLinked Entities in the Question:")
for entity, link in question_entity_links.items():
<<<<<<< HEAD
    print(f"{entity}: {link}")
>>>>>>> 2db3c16 (entity linker)
=======
    print(f"{entity}: {link}")
>>>>>>> b27be16 (made it dynamic, fixed formatting in the output, added cardinal in the omit_labels list)
