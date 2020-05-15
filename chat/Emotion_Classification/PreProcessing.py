import re
import nltk
from nltk.stem import WordNetLemmatizer
from time import time
from emoji import demojize

lemmatizer=WordNetLemmatizer()

def preprocess(texts, quiet=False):
  start = time()
  texts = texts.str.lower()

  # Remove special chars    
  texts = texts.str.replace(r"(http|@)\S+", " ")
  texts = texts.apply(demojize)    
  texts = texts.str.replace(r"’","'")
  texts = texts.str.replace("n't"," not")
  texts = texts.str.replace("'ll"," will")
  texts = texts.str.replace("'ve"," have")
  texts = texts.str.replace(r"[^a-z\':_]", " ")
  texts = texts.str.replace("re-[a-z]+"," ")
  
  # Remove repetitions
  pattern = re.compile(r"(.)\1{2,}", re.DOTALL)
  texts = texts.str.replace(pattern, r"\1")

  # Remove stop words
  stopwords = nltk.corpus.stopwords.words('english')
  stopwords.remove('not')
  stopwords.remove('nor')
  stopwords.remove('no')
  texts = texts.apply(
    lambda x: ' '.join([word for word in x.split() if word not in stopwords])
  )
  texts = texts.apply(lambda x: " ".join([lemmatizer.lemmatize(word) for word in x.split()]))

  if not quiet:
    print("Time to clean up: {:.2f} sec".format(time() - start))

  return texts