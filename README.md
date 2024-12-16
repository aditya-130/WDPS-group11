# WDPS-group11

Python program to process language model outputs, extract answers and validate them against online knowledge bases.

Mount project to docker image:

```jsx
docker run -ti -v <path_to_project_folder>:/workspace karmaresearch/wdps2
```

Go to workspace:

```jsx
cd / workspace / WDPS - group11;
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

Download

```jsx
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_md
```
