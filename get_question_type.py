import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

def preprocess(text):
    #Tokenizes and performs part-of-speech tagging on text
    tokens = word_tokenize(text)
    return pos_tag(tokens)

def determine_question_type(question):
    #Determines if the question is an entity question or a yes/no question
    tagged_tokens = preprocess(question)
    wh_pronouns = [token for token, tag in tagged_tokens if tag in ('WP', 'WDT', 'WP$', 'WRB')]
    return 'entity' if wh_pronouns else 'y/n'