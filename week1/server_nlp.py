from fastapi import FastAPI

# NLP library imports
from transformers import pipeline

# Generate pipeline
transformer_pipe = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

# FASTAPI app
app = FastAPI()

# response format {result: [{label: x, score: y}]}
@app.post("/analyse/{text}")
async def analyse(text):
	result = transformer_pipe(text)
	return {"result": result }
