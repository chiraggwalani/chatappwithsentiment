import PreProcessing
import joblib
import numpy as np
import pandas as pd

model = joblib.load('Emo_model.pkl')  
vectorizer = joblib.load('Emo_vect.pkl')
label=joblib.load('Emo_label.pkl')

pred_data = pd.Series("i bit my lip as he slightly whispered this will feel weird tell me if i hurt you")
pred_data=PreProcessing.preprocess(pred_data)
pred_vect=vectorizer.transform(pred_data)
y_pred = model.predict_proba(pred_vect)

for index, value in enumerate(np.sum(y_pred, axis=0) / len(y_pred)*100):
    print(label.classes_[index]+" : "+"{:.2f}".format(value))

