# Lightweight Python base image (same major.minor version as the training environment)
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the API code, the requirements file and the serialized model into the container
COPY . .

# Install the dependencies without caching to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# The API listens on port 7860 inside the container
EXPOSE 7860

# Start the Flask app with Gunicorn: 4 worker processes, bound to all interfaces on port 7860
# - `app:superkart_api` -> the Flask instance named `superkart_api` inside app.py
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "--timeout", "120", "app:superkart_api"]
