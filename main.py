from extract_answer import extract_answer
from entity_linker import get_entities
from llama_cpp import Llama
from factChecker import verifyAnswer

model_path = "../../home/user/models/llama-2-7b.Q4_K_M.gguf"

if __name__ == "__main__":
    llm = Llama(model_path=model_path, verbose=False)

    file1 = open("output.txt","w")

    with open("input.txt", "r") as file2:   #change file name if needed
        for line in file2:

            question_id = "".join(line.split(" ")[0])
            question = " ".join(line.split(" ")[1:]).strip()
            print(question_id,"\t",question)

            print(f"Asking the question to Llama model (wait, it can take some time...)")
            output = llm(question, max_tokens=64)
            raw_text = output['choices'][0]['text']
            raw_text = question_id + "\tR" + raw_text + "\n" 
            print("Raw text generated")

            extracted_entities = get_entities(question,raw_text)
            print("Entities extracted successfully")
            question_entities = ""
            for ent in extracted_entities['question_entities']:
                temp = question_id + "\tE\t" + ent[0] + "\t" + ent[1] + "\n"
                question_entities += temp

            answer_entities = ""
            for ent in extracted_entities['answer_entities']:
                temp = question_id + "\tE\t" + ent[0] + "\t" + ent[1] + "\n"
                answer_entities += temp

            extracted_answer = " ".join(extract_answer(question, raw_text))
            extracted_answer = question_id + "\tA\t" + extracted_answer + "\n"
            print("Answer extracted")

            correctness_of_answer = verifyAnswer(question,extracted_answer,extracted_entities)
            correctness_of_answer = question_id + "\tC\t" + correctness_of_answer + "\n"
            print("Correctness checked")

            final_output = raw_text + extracted_answer + correctness_of_answer + question_entities + answer_entities 
            print("Output written to output.txt successfully")

            file1.write(final_output)

    file1.close()
