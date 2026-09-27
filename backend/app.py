# SuperKart sales prediction - Flask REST API (backend)

import os
import joblib                                        # for loading the serialized model pipeline
import pandas as pd                                  # for building the model input
from flask import Flask, request, jsonify            # for creating the REST API

# Initialize the Flask app
superkart_api = Flask("SuperKart Sales Predictor")

# Load the trained pipeline (one-hot encoder + regressor) once, when the server starts
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "superkart_model.joblib")
model = joblib.load(MODEL_PATH)

# The exact features (and order) the model was trained on
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Home route - used as a health check
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Prediction API"


# Online inference: predict the sales of a single product-store record sent as JSON
@superkart_api.post("/v1/predict")
def predict_sales():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Build a one-row DataFrame in the training column order
    input_data = pd.DataFrame([{f: data[f] for f in FEATURES}])

    prediction = model.predict(input_data).tolist()[0]

    return jsonify({"Sales": round(float(prediction), 2)})


# Batch inference: predict the sales for every row of an uploaded CSV file
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file in the 'file' form field"}), 400

    input_data = pd.read_csv(request.files["file"])

    missing = [f for f in FEATURES if f not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing columns in CSV: {missing}"}), 400

    predictions = model.predict(input_data[FEATURES]).tolist()

    # Map each row index to its predicted sales
    output_dict = {str(i): round(float(pred), 2) for i, pred in enumerate(predictions)}

    return jsonify(output_dict)


# Run the Flask app (development server). In the container the app is served by Gunicorn instead.
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=True)
