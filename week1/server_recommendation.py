from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
import pickle
from typing import Dict, Any
from pydantic import BaseModel


from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

# Request type
class Transaction(BaseModel):
    data: Dict[str, Any]

# FastAPI app
app = FastAPI()

# Load data
print("Loading data...")
metadata = pd. read_csv('./data/movies_metadata.csv', low_memory=False)
print("Loaded metadata!")
links = pd.read_csv('./data/links_small.csv')
print("Loaded links!")

links = links[links['tmdbId'].notnull()]['tmdbId'].astype('int')

# Remove some weird values
metadata = metadata.drop([19730, 29503, 35587])

# Convert ID to int
metadata['id'] = metadata['id'].astype('int')

# Select the movies we have in links (subset)
subdata = metadata[metadata['id'].isin(links)]

subdata['tagline'] = subdata['tagline'].fillna('')

# Create a description feature for simplicity
subdata['description'] = subdata['overview'] + subdata['tagline']
subdata['description'] = subdata['description'].fillna('')

print("Creating TFIDF/Cosine implementations...")
tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0.0, stop_words='english')

print("TFIDF Fitting...")
tfidf_matrix = tf.fit_transform(subdata['description'])
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Connect titles with appropriate data indexes
subdata = subdata.reset_index()
titles = subdata['title']
indices = pd.Series(subdata.index, index=subdata['title'])

print("Ready.")

def get_recommendations(title, res):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:res + 1]
    movie_indices = [i[0] for i in sim_scores]
    return titles.iloc[movie_indices]

@app.post("/recommend")
def predict_anomalies(request: Transaction):
    try:
        # Process data
        movie = (request.data)["movie"]
        amount = (request.data)["amount"]
        recommendations = get_recommendations(movie, amount)
        # print(recommendations)

        # Send data
        return {"result": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))