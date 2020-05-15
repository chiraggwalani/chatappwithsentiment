import re
import spacy
import joblib
from emoji import demojize
from spacy.tokenizer import Tokenizer
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS

nlp = English()
tokenizer = Tokenizer(nlp.vocab)

model = joblib.load('chat/Emo_model.pkl')  
vectorizer = joblib.load('chat/Emo_vect.pkl')
label=joblib.load('chat/Emo_label.pkl')

def preprocess(texts):
    
    texts = str(texts)
    texts = texts.lower()
    texts = re.sub(r"(http|@)\S+", " ",texts)
    texts = demojize(texts)   
    texts = re.sub(r"’","'",texts)
    texts = re.sub("n't","n not",texts)
    texts = re.sub("'ll"," will",texts)
    texts = re.sub("'ve"," have",texts)
    texts = re.sub(r"[^a-z\':_]", " ",texts)
    texts = re.sub(r"[0-9]+", " ",texts)
    texts = re.sub("re-[a-z]+"," ",texts)
    pattern = re.compile(r"(.)\1{2,}", re.DOTALL)
    texts = re.sub(pattern, r"\1",texts)

    tokens = tokenizer(texts)
    try:
        STOP_WORDS.remove('not')
        STOP_WORDS.remove('nor')
        STOP_WORDS.remove('no')
    except:
        pass

    lemma_list = []
    for token in tokens:
        if token not in STOP_WORDS:
            lemma_list.append(token.lemma_)
    texts = ' '.join(map(str,lemma_list))
    pred_vect=vectorizer.transform([texts])
    texts=label.classes_[model.predict(pred_vect)]
    texts = ' '.join(map(str,texts))

    return texts