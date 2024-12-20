from extract_answer import extract_answer
from entity_linker import get_entities
from llama_cpp import Llama
from factChecker import verifyAnswer
from get_question_type import determine_question_type

model_path = "../../home/user/models/llama-2-7b.Q4_K_M.gguf"

if __name__ == "__main__":
    llm = Llama(model_path=model_path, verbose=False)

    output_file = open("output.txt","w")

    with open("input.txt", "r") as input_file:   #change file name if needed
        for line in input_file:

            question_id = "".join(line.split(" ")[0])
            question = " ".join(line.split(" ")[1:]).strip()
            print(question_id,"\t",question)

            print(f"Asking the question to Llama model (wait, it can take some time...)")
            output = llm(question, max_tokens=64)
            raw_text = output['choices'][0]['text']
            print("Raw text generated: ", raw_text)
            
            extracted_entities = get_entities(question,raw_text)
            print("Entities extracted" )
            print("Entities in question: ", extracted_entities["question_entities"])
            print("Entities in answer: ", extracted_entities["answer_entities"])

            extracted_answer = extract_answer(question, raw_text, extracted_entities)
            if (extracted_answer in ['Yes','No','No answer found']):
                answer = extracted_answer
                print("Answer extracted: ", answer)
                extracted_answer = question_id + "\tA\t" + extracted_answer + "\n"
            else:
                answer = extracted_answer[0]
                print("Answer extracted: ", extracted_answer)
                extracted_answer = question_id + "\tA\t" + extracted_answer[1] + "\n"
                
            correctness_of_answer = verifyAnswer(question,answer,extracted_entities)
            print("Check correctness: ", correctness_of_answer)
            
            raw_text = question_id + "\tR" + raw_text + "\n"
            correctness_of_answer = question_id + "\tC\t" + correctness_of_answer + "\n"

            question_entities = ""
            for ent in extracted_entities['question_entities']:
                temp = question_id + "\tE\t" + ent[0] + "\t" + ent[1] + "\n"
                question_entities += temp
            
            answer_entities = ""
            for ent in extracted_entities['answer_entities']:
                temp = question_id + "\tE\t" + ent[0] + "\t" + ent[1] + "\n"
                answer_entities += temp

            final_output = raw_text + extracted_answer + correctness_of_answer + question_entities + answer_entities 
            output_file.write(final_output)
            print("Output written to output.txt successfully", "\n")

    output_file.close()
