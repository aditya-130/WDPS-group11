# Llama
from llama_cpp import Llama

# Spacy
import spacy

model_path = "models/llama-2-7b.Q4_K_M.gguf"

question = input('Write a question: ')
llm = Llama(model_path=model_path, verbose=False)
print("Asking the question \"%s\" to %s (wait, it can take some time...)" % (question, model_path))
output = llm(
      question, # Prompt
      max_tokens=64,
      stop = ['Q:', '?']
      # stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
      # echo=True # Echo the prompt back in the output
)
print("Here is the output")
answer = output['choices'][0]['text']
print(output['choices'][0]['text']) 

print('the question was:', question)


nlp = spacy.load('en_core_web_lg')

ent_list = nlp(answer)
question_entities = nlp(question)

print('Entities:')
for ent in ent_list.ents:
      print(ent.text, ent.label_)

print('Entities in the question:')
for q_ent in question_entities.ents:
      print(q_ent.text, q_ent.label_)