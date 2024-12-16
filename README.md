# WDPS-group11
Python program to process language model outputs, extract answers and validate them against online knowledge bases.

Mount project to docker image:

```jsx
docker run -ti -v /Users/aksharabruno/WDPS:/workspace karmaresearch/wdps2
```

Go to workspace:

```jsx
cd /workspace/WDPS-group11
```

Install requirements:

```jsx
pip install -r requirements.txt
```

Download
```jsx
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_md
```
