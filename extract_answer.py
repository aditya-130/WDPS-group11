import spacy
from get_question_type import determine_question_type

nlp = spacy.load('en_core_web_lg')

def extract_entity_answer(question, answer):
    #Extracts the probable entity answer from the LLM response
    probable_answers = []
    answer_entities = [(ent.text, ent.label_, token.pos_) 
                        for ent in nlp(answer).ents for token in ent]
    question_entities = [(ent.text, ent.label_) 
                         for ent in nlp(question).ents]
    question_entity_texts = [text for text, label in question_entities]
    question_entity_labels = [label for text, label in question_entities]
    #print(answer_entities)
    for entity_text, entity_label, pos in answer_entities:
        # Assumption: An entity is the answer if it doesn't exist in the question and if its label is also a label an entity in the question. 
        # I also want to map LOC with GPE
        if entity_text not in question_entity_texts and (entity_label in question_entity_labels or \
                                                         (entity_label in ('GPE', 'LOC') and any(l in ('GPE', 'LOC') for l in question_entity_labels))) and \
                                                            entity_text not in probable_answers:            
            probable_answers.append(entity_text)  # Add only the text

    return probable_answers

def extract_yes_or_no(question, answer):
    """Extracts a yes/no answer from the LLM response."""
    if any(phrase in answer.lower() for phrase in ["the answer is no", "no, it is not", "obviously not"]): # Check for hand build patterns
        return 'No'
    
    if any(phrase in answer.lower() for phrase in ["yes,"]): # Check for hand build patterns
        return 'Yes'

    answer_entities = [ent.text for ent in nlp(answer).ents]
    question_entities = [ent.text for ent in nlp(question).ents]
    matching_entities = [ent for ent in answer_entities if ent in question_entities] # Entities that are in both question and answer

    negated = any(check_negation(ent, answer) for ent in matching_entities) # Check if mathcing entities are negated. e.g. Is Athens the capital of Italy? No Athens isn't the capital of Italy
    if negated:
        return 'No' 

    # Pairs approach: To handle cases like: Q: Is Paris the capital of Germany, A: Berlin is the capital of Germany, Paris is the capital of France.
    # The reason for this is that in those types of answers no signs of negation exist
    question_pairs = find_entity_pairs(question)
    answer_pairs = find_entity_pairs(answer)
    if len(question_pairs) > 0 and len(answer_pairs) > 0:
        if any(pair in answer_pairs for pair in question_pairs):
            return 'Yes'
        else:
            return 'No'
    

def check_negation(entity, text):
    """Checks if an entity is negated in the given text."""
    doc = nlp(text)
    negation_cues = ["not", "no", "never", "n't", "without"]
    entity_span = doc.char_span(text.index(entity), text.index(entity) + len(entity))
    if entity_span is not None:
        for token in entity_span.doc[entity_span.start - 3 : entity_span.end + 3]:
            if token.text.lower() in negation_cues:
                return True
    return False

def find_entity_pairs(text):
    """Finds pairs of entities in the text."""
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

def extract_answer(question, answer):
    """Extracts the answer based on the question type."""
    question_type = determine_question_type(question)
    print('Question type:', question_type)
    if question_type == 'entity':
        return extract_entity_answer(question, answer)
    elif question_type == 'y/n':
        return extract_yes_or_no(question, answer)
