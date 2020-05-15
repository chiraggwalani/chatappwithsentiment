from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
import PreProcessing
import numpy as np
import pandas as pd
from tqdm import tqdm
import joblib
import time
import re

data_df = pd.read_csv('emotion.csv')
data_df.emotions.value_counts()

group=data_df.groupby(data_df['emotions'])
data=pd.concat([group.get_group("joy")[:20000], group.get_group("fear")[:20000], group.get_group("love")[:20000], group.get_group("anger")[:20000] , group.get_group("sadness")[:20000],group.get_group("surprise") ])
data.sample(frac=1)
x=data['text']
x=PreProcessing.preprocess(x)

tfidf = TfidfVectorizer(max_features=10000, analyzer='word',max_df=0.7,min_df=0.0001)
X= tfidf.fit_transform(x)

lbl_enc = preprocessing.LabelEncoder()
y = lbl_enc.fit_transform(data.emotions.values)

X_train, X_val, y_train, y_val = train_test_split(X, y, stratify=y, random_state=42, test_size=0.1, shuffle=True)

nb = MultinomialNB()
nb.fit(X_train, y_train)
y_pred = nb.predict(X_val)
print('naive bayes tfidf accuracy %s' % accuracy_score(y_pred, y_val))

joblib.dump(tfidf,'Emo_vect.pkl')
joblib.dump(nb,'Emo_model.pkl')
joblib.dump(lbl_enc,'Emo_label.pkl')

pred_data = pd.Series("i bit my lip as he slightly whispered this will feel weird tell me if i hurt you")
pred_data=PreProcessing.preprocess(pred_data)
pred_vect=tfidf.transform(pred_data)
y_pred = nb.predict_proba(pred_vect)

for index, value in enumerate(np.sum(y_pred, axis=0) / len(y_pred)*100):
    print(lbl_enc.classes_[index]+" : "+"{:.2f}".format(value))