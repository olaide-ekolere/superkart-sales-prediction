# Lightweight Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Streamlit app and its requirements into the container
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Streamlit listens on port 8501
EXPOSE 8501

# Run the Streamlit app, reachable from outside the container.
# XSRF protection is disabled so that file uploads work through the Codespaces port-forwarding proxy.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
