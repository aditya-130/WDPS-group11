# Llama
from llama_cpp import Llama

# Nltk
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

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


# Nltk
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

def preprocess(txt):
    txt = nltk.word_tokenize(txt)
    txt = nltk.pos_tag(txt)
    return txt




ans_tk = preprocess(answer)
ans_tk_clean = []
nn_a = [] # list of nouns
nnp_a = [] # list of proper nouns
for a in ans_tk:
      if a not in ans_tk_clean:
            ans_tk_clean.append(a)
            # print(a)
            if a[1] == 'NN' or a[1] == 'NNS': # get nouns
                  nn_a.append(a)
            if a[1] == 'NNP' or a[1] == 'NNPS': # get proper nouns
                  nnp_a.append(a)

que_tk = preprocess(question)

que_tk_clean = []

nn_q = [] # list of nouns 
nnp_q = [] # list of proper nouns
wp_q = [] # list of wh- pronouns
for q in que_tk:
      if q not in que_tk_clean:
            que_tk_clean.append(q)
            # print(q)
            if q[1] == 'WP' or q[1] == 'WDT' or q[1] == 'WP$' or q[1] == 'WRB': # get  wh- pronouns, to determine if I'm looking for a Yes/No or entity.
                  wp_q.append(q)
            if q[1] == 'NN' or q[1] == 'NNS': # get nouns
                  nn_q.append(q)
            if q[1] == 'NNP' or q[1] == 'NNPS': # get proper nouns
                  nnp_q.append(q)

if wp_q:
      print('Wh- pronouns in question are:' , wp_q)
else:
      print('No wh- pronouns, in the question which indicates that the answer should be an entity')

print('Nouns in the question:', nn_q)
print('Proper nouns in the question:', nnp_q)

print('Nouns in the answer:', nn_a)
print('Proper nouns in the answer:', nnp_a)