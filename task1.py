from llama_cpp import Llama
import spacy
import requests
import os
import sys

def search_wikipedia(entity_name, entity_label):
    """Searches Wikipedia for a given entity and returns the URL of the top result."""
    search_url = f"https://en.wikipedia.org/w/api.php"
    entity_name = entity_name.replace(" ", "_")
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
    response = requests.get(search_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        search_results = data['query']['search']
        
        if search_results:
            top_result_title = search_results[0]['title']
            return f"https://en.wikipedia.org/wiki/{top_result_title.replace(' ', '_')}"
    
    return None

def link_entities_to_wikipedia(text):
    """Identifies named entities in a text and links them to Wikipedia."""
    doc = nlp(text)
    entity_links = {}
    omit_labels = {"DATE", "TIME", "MONEY", "PERCENT", "CARDINAL"}
    for ent in doc.ents:
        entity_name = ent.text
        entity_label = ent.label_
        
        if entity_label in omit_labels:
            continue
        
        link = search_wikipedia(entity_name, entity_label)
        if link:
            entity_links[ent.text] = link
    return entity_links

def process_questions_from_file(input_filename, output_filename):
    """Reads questions from a file, generates answers, and writes them to another file."""
    with open(input_filename, 'r') as infile, open(output_filename, 'w') as outfile:
        for line in infile:
            try:
                question_id, question_text = line.strip().split('\t')
                output = llm(question_text, max_tokens=128)
                answer = output['choices'][0]['text']

                outfile.write(f'{question_id}\tR"{answer}"\n')

                answer_entity_links = link_entities_to_wikipedia(answer)
                for entity, link in answer_entity_links.items():
                    outfile.write(f'{question_id}\tE"{entity}"\t{link}\n')  
            except ValueError:
                print(f"Skipping invalid line: {line.strip()}")

if __name__ == "__main__":
    sys.stderr = open(os.devnull, 'w')  # Suppress warnings

    model_path = "models/llama-2-7b.Q4_K_M.gguf"  # Replace with your model path
    llm = Llama(model_path=model_path, verbose=False)
    nlp = spacy.load('en_core_web_lg')

    input_filename = "input.txt"  # Replace with your input file
    output_filename = "output.txt"  # Replace with your desired output file

    process_questions_from_file('input.txt', 'output_file')
