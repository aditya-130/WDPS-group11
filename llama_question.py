from llama_cpp import Llama
model_path = "models/llama-2-7b.Q4_K_M.gguf"

question = input('Ask a question: ')
llm = Llama(model_path=model_path, verbose=False)
print("Asking the question \"%s\" to %s (wait, it can take some time...)" % (question, model_path))
output = llm(
      question, # Prompt
      max_tokens=512,
      stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
      echo=True # Echo the prompt back in the output
)
print("Here is the output")
print(output['choices'][0]['text']) 
