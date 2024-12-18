import spacy
from get_question_type import determine_question_type

nlp = spacy.load('en_core_web_lg')

def extract_entity_answer(question, dicts):
    print('extract_entity_answer is called')
    """Extracts the probable entity answer from the LLM response."""
    probable_answers = []
    answer_entities = dicts['answer_entities']
    question_entities = dicts['question_entities']

    # print(question_entities, answer_entities)

    # Identify question type based on keywords
    question_type = None
    if any(keyword in question.lower() for keyword in ["who", "whose", "whom"]):
        question_type = "PERSON"
    elif "where" in question.lower():
        question_type = "GPE_LOC"

    # Extract probable answers
    for entity in answer_entities:
        # Observation: Probable answers are entities in the answer that don'tt exist in the question
        if entity not in question_entities:
            probable_answers.append((entity[0], entity[1], entity[2], entity[3]))  # Add text and label

    # print('Probable answers before filtering:', probable_answers)

    # Filter based on question type if applicable
    if question_type == "PERSON":
        probable_answers = [(text, link, score, label) for text, link, score, label in probable_answers if label == "PERSON"]
    elif question_type == "GPE_LOC":
        probable_answers = [(text, link, score, label) for text, link, score, label in probable_answers if label in ["GPE", "LOC"]]

    # Remove duplicate entities
    probable_answers = list(dict.fromkeys(probable_answers))

    # print('Probable answers after filtering:', probable_answers)
    if len(probable_answers) == 1:
        return probable_answers[0][1]  # Return the link of the only probable answer
    elif len(probable_answers) > 1:
        # Sort by score and return the link of the one with the highest score
        best_answer = max(probable_answers, key=lambda x: x[2])  # x[2] is the score
        return best_answer[1]  # Return the link of the answer with the highest score
    else:
        return ['no answer found']


def extract_yes_or_no(question, answer, dicts):
    #Extracts a yes/no answer from the LLM response
    if any(phrase in answer.lower() for phrase in ["the answer is no", "no, it is not", "obviously not"]): # Check for hand build patterns
        return ['No']
    
    if any(phrase in answer.lower() for phrase in ["yes,"]): # Check for hand build patterns
        return ['Yes']

    answer_entities = dicts['answer_entities']
    question_entities = dicts['question_entities']
    matching_entities = [ent[0] for ent in answer_entities if ent in question_entities] # Entities that are in both question and answer

    negated = any(check_negation(ent, answer) for ent in matching_entities) # Check if mathcing entities are negated. e.g. Is Athens the capital of Italy? No Athens isn't the capital of Italy
    if negated:
        return ['No'] 

    # Pairs approach: To handle cases like: Q: Is Paris the capital of Germany, A: Berlin is the capital of Germany, Paris is the capital of France.
    # The reason for this is that in those types of answers no signs of negation exist
    question_pairs = find_entity_pairs(question)
    answer_pairs = find_entity_pairs(answer)

    question_pairs = {tuple(sorted(pair)) for pair in question_pairs}
    answer_pairs = {tuple(sorted(pair)) for pair in answer_pairs}

    if len(question_pairs) > 0 and len(answer_pairs) > 0:
        print('Pairs:', question_pairs, answer_pairs)
        if any(pair in answer_pairs for pair in question_pairs):
            return ['Yes']
        else:
            return ['No']
        
    return 'No' # We consider unclear answers as negative
    

def check_negation(entity, text):
    #Checks if an entity is negated in the given text
    doc = nlp(text)
    negation_cues = ["not", "no", "never", "n't", "without"]
    entity_span = doc.char_span(text.index(entity), text.index(entity) + len(entity))
    if entity_span is not None:
        for token in entity_span.doc[entity_span.start - 3 : entity_span.end + 3]:
            if token.text.lower() in negation_cues:
                return True
    return False

def find_entity_pairs(text):
    #Finds pairs of entities in the text
    doc = nlp(text)  # Process the text with spaCy
    entities = [ent.text for ent in doc.ents]  # Extract all entities
    pairs = []
    for i in range(len(entities) - 1):  # Iterate through entities
        for j in range(i + 1, len(entities)):  # Iterate through remaining entities
            if entities[i] not in [p[0] for p in pairs] and entities[i] not in [p[1] for p in pairs] and \
               entities[j] not in [p[0] for p in pairs] and entities[j] not in [p[1] for p in pairs]:
                # Check distance between entities
                start_i = text.index(entities[i]) + len(entities[i])
                start_j = text.index(entities[j])
                words_between = len(text[start_i:start_j].split())
                if words_between <= 5:
                    pairs.append((entities[i], entities[j]))  # Create pairs
                    break  # Move to the next entity
    return pairs

def extract_answer(question, answer, entities):
    #Extracts the answer based on the question type
    question_type = determine_question_type(question)
    print('Entities:', entities)
    print('Question type:', question_type)
    if question_type == 'entity':
        return extract_entity_answer(question, entities)
    elif question_type == 'y/n':
        return extract_yes_or_no(question, answer, entities)

