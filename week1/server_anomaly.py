import os
from sklearn.preprocessing import RobustScaler
from fastapi import FastAPI, HTTPException
import pickle
from pydantic import BaseModel
from typing import Dict, Any
import pandas as pd

# Request type
class Transaction(BaseModel):
    data: Dict[str, Any]

# FastAPI app
app = FastAPI()

# Load model
with open("iforest.pkl", "rb") as file:
    model = pickle.load(file)

@app.post("/predict")
def predict_anomalies(request: Transaction):
    """Predict anomalies for the incoming data."""
    try:
        # Process data
        scaler = RobustScaler()
        df = pd.DataFrame(request.data, index=[0])
        df['amount_s'] = scaler.fit_transform(df['Amount'].values.reshape(-1,1))
        df = df.drop(columns=['Time', 'Amount'])
        
        # Predict
        prediction = (model.predict(df))[0]
        
        # Adjust
        if prediction == 1: 
            prediction = 0 
        elif prediction == -1: 
            prediction = 1

        # Send data
        return {"result": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))