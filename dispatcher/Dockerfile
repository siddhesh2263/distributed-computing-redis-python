FROM python:3.10-slim

# Set working directory inside the container:
WORKDIR /app

# Copy app files:
COPY app.py .
COPY requirements.txt .

# Install dependencies:
RUN pip install --no-cache-dir -r requirements.txt

# # Run the Flask app using Gunicorn (2 worker processes)
# CMD ["gunicorn", "app:app", "-w", "2", "-b", "0.0.0.0:5000"]

# Use Flask's built-in server for testing
CMD ["python", "app.py"]