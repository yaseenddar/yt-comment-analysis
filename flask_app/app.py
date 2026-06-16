from flask import Flask,request,jsonify,send_file
from flask_cors import CORS
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import joblib 
import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import matplotlib.dates as mdates


app = Flask(__name__)
CORS(app)

def load_model_and_vectorizer_from_local(model_path,vectorizer_path):
    

    # Load the model from local
    model = joblib.load(model_path)
    
    vectorizer = joblib.load(vectorizer_path)
    return model,vectorizer

# Initailize the model and cvectorizer
model , vectorizer = load_model_and_vectorizer_from_local('./lgbm_model.pkl','./tfidf_vectorizer.pkl')


def preprocess_comment(comment):
    """Apply preprcessing transformation to a commetn."""
    try:
        # Convert to lowercase
        comment = comment.lower()
        print()
        # Remove trailing and leading whitespaces
        comment = comment.strip()
        
        #  Remove newine characters
        # comment = re.sub((r'\n',' ',comment))
        comment = re.sub(r'\n', ' ', comment)
        # Remove non-alphanumeric characters, exept punctuatuation
        comment = re.sub(r'[^A-Za-z0-9\s!?.,]','',comment)

        # Remove stopwords but retain important ones for sentiment analysis
        stop_words = set(stopwords.words('english')) - {'not','but','however','not','yet'}
        comment = ' '.join([word for word in comment.split() if word not in stop_words])

        # Lemmatizer the words
        lemmatizer = WordNetLemmatizer()
        comment = ' '.join([lemmatizer.lemmatize(word) for word in comment.split()])

        return comment
    except Exception as e:
        print(f"Error in preprocessing comment: {e}")
        raise
    

@app.route('/predict',methods=['POST'])
def predict():
    data = request.json
    comments = data.get('comments')
    
    if not comments:
        return jsonify({"error": "No comments provided"}), 400

    try:
        # Preprocess each comment before vectorizing
        preprocessed_comments = [preprocess_comment(comment) for comment in comments]
        
        # Transform comments using the vectorizer
        transformed_comments = vectorizer.transform(preprocessed_comments)
        
        # Make predictions
        predictions = model.predict(transformed_comments).tolist()  # Convert to list
        
        # Convert predictions to strings for consistency
        predictions = [str(pred) for pred in predictions]
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
    
    # Return the response with original comments and predicted sentiments
    response = [{"comment": comment, "sentiment": sentiment} for comment, sentiment in zip(comments, predictions)]
    print(response)
    return jsonify(response)
