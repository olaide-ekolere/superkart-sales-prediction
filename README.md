# SuperKart Sales Prediction

End-to-end deployment of a sales forecasting model for SuperKart.

- **Model**: Random Forest (tuned) pipeline (one-hot encoding + regressor) trained on the SuperKart product-store dataset.
- **backend/** - Flask REST API served with Gunicorn on port 7860 (`POST /v1/predict`, `POST /v1/predictbatch`).
- **frontend/** - Streamlit UI on port 8501 that calls the API for single and batch predictions.

## Run both services in a GitHub Codespace

```bash
cd backend
docker build -t superkart-backend .
cd ../frontend
docker build -t superkart-frontend .

docker network create superkart-network
docker run -d --name backend  --network superkart-network -p 7860:7860 superkart-backend
docker run -d --name frontend --network superkart-network -p 8501:8501 superkart-frontend
```

Then set ports **7860** and **8501** to *Public* in the Codespace **Ports** tab and open the port-8501 URL.
