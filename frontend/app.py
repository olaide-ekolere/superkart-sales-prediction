# SuperKart sales prediction - Streamlit frontend

import os
import requests
import pandas as pd
import streamlit as st

# Base URL of the Flask backend. Inside the Docker network the backend container is reachable as "backend".
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒", layout="centered")

st.title("🛒 SuperKart Sales Forecasting System")
st.write(
    "Forecast the total revenue a product will generate in a given store for the upcoming quarter. "
    "Use the form for a single product-store combination, or upload a CSV file to score many records at once."
)

with st.sidebar:
    st.header("About")
    st.write(
        "The frontend sends your inputs to a Flask REST API that hosts the trained "
        "regression pipeline (one-hot encoding + tree-based ensemble)."
    )
    st.write("Backend URL:", f"`{BACKEND_URL}`")
    if st.button("Check API status"):
        try:
            r = requests.get(BACKEND_URL + "/", timeout=10)
            st.success(r.text if r.status_code == 200 else f"API returned status {r.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Cannot reach the API: {e}")

# ---------------------------------------------------------------- Online (single) prediction
st.header("Online Prediction")
st.caption("Enter the product and store details, then click Predict.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Product details")
    Product_Weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
    Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    Product_Allocated_Area = st.number_input(
        "Product Allocated Area (share of store display area)", min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f"
    )
    Product_MRP = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=117.08, step=0.01)
    Product_Id_char = st.selectbox(
        "Product Family (Product ID prefix)", ["FD", "DR", "NC"],
        help="FD = Food, DR = Drinks, NC = Non-consumables",
    )
    Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])
with col2:
    st.subheader("Store details")
    Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
    Store_Type = st.selectbox(
        "Store Type", ["Supermarket Type1", "Supermarket Type2", "Supermarket Type3", "Departmental Store", "Food Mart"]
    )
    Store_Age_Years = st.number_input("Store Age (Years)", min_value=0, max_value=100, value=16, step=1)

product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": int(Store_Age_Years),
    "Product_Type_Category": Product_Type_Category,
}

if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data, timeout=30)
        if response.status_code == 200:
            predicted_sales = response.json()["Sales"]
            st.success(f"Predicted Product Store Sales Total: **{predicted_sales:,.2f}**")
            with st.expander("Input sent to the API"):
                st.json(product_data)
        else:
            st.error(f"API error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to connect to the prediction API: {e}")

# ---------------------------------------------------------------- Batch prediction
st.header("Batch Prediction")
st.caption(
    "Upload a CSV file with the columns: Product_Weight, Product_Sugar_Content, Product_Allocated_Area, Product_MRP, "
    "Store_Size, Store_Location_City_Type, Store_Type, Product_Id_char, Store_Age_Years, Product_Type_Category."
)

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    batch_df = pd.read_csv(uploaded_file)
    st.write(f"Preview of the uploaded file ({batch_df.shape[0]} rows):")
    st.dataframe(batch_df.head(), use_container_width=True)

    if st.button("Predict for Batch", type="primary"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": batch_df.to_csv(index=False).encode("utf-8")},
                timeout=120,
            )
            if response.status_code == 200:
                results = response.json()
                predictions = pd.Series(results, name="Predicted_Sales").astype(float)
                predictions.index = predictions.index.astype(int)
                results_df = batch_df.copy()
                results_df["Predicted_Sales"] = predictions.sort_index().values

                st.success("Predictions completed successfully!")
                st.subheader("Batch Prediction Results")
                st.dataframe(results_df, use_container_width=True)

                st.metric("Total predicted sales for the batch", f"{results_df['Predicted_Sales'].sum():,.2f}")

                st.download_button(
                    "Download predictions as CSV",
                    data=results_df.to_csv(index=False).encode("utf-8"),
                    file_name="superkart_batch_predictions.csv",
                    mime="text/csv",
                )
            else:
                st.error(f"API error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Unable to connect to the prediction API: {e}")
