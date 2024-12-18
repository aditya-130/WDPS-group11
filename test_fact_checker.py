#TEST 1

from fact_checker import factCheckPipeline


text = "Seoul is the capital of South Korea"
sbj = "http://yago-knowledge.org/resource/Seoul"
obj = "http://yago-knowledge.org/resource/South_Korea"


a = factCheckPipeline(sbj, obj, text)

text = "Busan is the capital of South Korea"
sbj = "http://yago-knowledge.org/resource/Busan"
obj = "http://yago-knowledge.org/resource/South_Korea"


a = factCheckPipeline(sbj, obj, text)

#TEST 2

text = "Shakespeare wrote Romeo and Juliet"
sbj = "http://yago-knowledge.org/resource/William_Shakespeare"
obj = "http://yago-knowledge.org/resource/Romeo_and_Juliet"

a = factCheckPipeline(sbj, obj, text)

text = "Shakespeare wrote War and Peace"
sbj = "http://yago-knowledge.org/resource/William_Shakespeare"
obj = "http://yago-knowledge.org/resource/War_and_Peace"

a = factCheckPipeline(sbj, obj, text)

text = "Tolstoy wrote Romeo and Juliet"
sbj = "http://yago-knowledge.org/resource/Leo_Tolstoy"
obj = "http://yago-knowledge.org/resource/Romeo_and_Juliet"

a = factCheckPipeline(sbj, obj, text)

#TEST 3

text = "Joe Biden is President of the United States"
sbj = "http://yago-knowledge.org/resource/Joe_Biden"
obj = "http://yago-knowledge.org/resource/United_States"

a = factCheckPipeline(sbj, obj, text)

text = "Elon Musk is President of the United States"
sbj = "http://yago-knowledge.org/resource/Joe_Biden"
obj = "http://yago-knowledge.org/resource/United_States"

a = factCheckPipeline(sbj, obj, text)
