# Imports
# Llama
from llama_cpp import Llama

# Nltk
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Simple Colors
from simple_colors import *

# scraping
import requests
from fake_useragent import UserAgent
 
import os
import sys

# Nltk Prerequisites 
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

def preprocess(txt):
    txt = nltk.word_tokenize(txt)
    txt = nltk.pos_tag(txt)
    return txt

def attempt_request(url: str, attempts: int = 3, text_output: bool = True) -> str:

    # headers
    ua = UserAgent(browsers="chrome", min_percentage=2.0)
    headers = {"User-Agent": str(ua.random)}

    # response placeholder
    response = None

    # loop over attempts
    for attempt in range(0, attempts):

        # if successful, stop attempts
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.status_code

        # if exception, check attempts
        except Exception as e:
            # if final attempt, stop attempts
            if attempt == attempts - 1:
                exception = str(e)
                break
            else:
                time.sleep(random.uniform(1, 3))
                continue

    # return None if request attempts failed
    if response == None:
        return None

sys.stderr = open(os.devnull, 'w')

# Ask question to llama
model_path = "models/llama-2-7b.Q4_K_M.gguf"

question = input('Write a question: ')
llm = Llama(model_path=model_path, verbose=False)
output = llm(
      question, # Prompt
      max_tokens=64,
      # stop = ['Q:', '?']
      # stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
      # echo=True # Echo the prompt back in the output
)
print('\033[1m' + "Input (A):", question, "\n" + '\033[0m')
answer = output['choices'][0]['text']
print('\033[1m' + "Text returned by the language model (B) (llama 2, 70B):"  + '\033[0m', output['choices'][0]['text']) 


answer_tokens = preprocess(answer)
disctinct_tokens = []
entities = [] # we assume entities are nouns and proper nouns | Tags: NN, NNS, NNP, NNPS

for token in answer_tokens:
      if token not in disctinct_tokens:
            disctinct_tokens.append(token)
            if token[1] == 'NN' or token[1] == 'NNS': # get nouns |NN, NNS tags are for nours such as objects
                  entities.append(token)
            if token[1] == 'NNP' or token[1] == 'NNPS': # get proper nouns | NNP, NNPS tags are usually for people, countries, cities, offices etc
                  entities.append(token)

question_tokens = preprocess(question)

for token in question_tokens:
      if token not in disctinct_tokens:
            disctinct_tokens.append(token)
            if token[1] == 'NN' or token[1] == 'NNS': # get nouns |NN, NNS tags are for nours such as objects
                  entities.append(token)
            if token[1] == 'NNP' or token[1] == 'NNPS': # get proper nouns | NNP, NNPS tags are usually for people, countries, cities, offices etc
                  entities.append(token)


wikipedia_entities = []
for entity in entities:
    wiki_link = f"https://en.wikipedia.org/wiki/{entity[0]}"
    if attempt_request(wiki_link):
         wikipedia_entities.append(entity)


print('\033[1m' + "Entities extracted:\n" + '\033[0m')
for wikipedia_entitiy in wikipedia_entities:
      wiki_link = f"https://en.wikipedia.org/wiki/{wikipedia_entitiy[0]}"

      print(wikipedia_entitiy[0], "     ", wiki_link, "\n")
