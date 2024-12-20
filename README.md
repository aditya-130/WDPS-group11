# WDPS-group11

Python program to process language model outputs, extract answers and validate them against online knowledge bases.

Mount project to docker image:

```jsx
docker run -ti -v <path_to_project_folder>:/workspace karmaresearch/wdps2
```

Go to workspace:

```jsx
cd /workspace/WDPS-group11
```

Install requirements:

```jsx
pip install -r requirements.txt
```

These are not installing when added to requirements.txt. Hence separate installation.

```jsx
python -m pip install -U sentence-transformers
pip install gensim
```

Download:

```jsx
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_md
python -m nltk.downloader punkt_tab
python -m nltk.downloader averaged_perceptron_tagger_eng
```

To run this application, run main.py. Output will be generated in output.txt file.

```jsx
python main.py
```
Note: Ensure adding input.txt to this folder before mounting this application. In case of a different file name, it can be renamed in main.py (line 14).