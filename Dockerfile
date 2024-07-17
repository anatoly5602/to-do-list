# Use the official Python image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if necessary (for tkinter or other packages)
RUN apt-get update && apt-get install -y \
    tk \
    libtk8.6

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Define the environment variable for Flask
ENV FLASK_APP=app.py

# Start the application using Gunicorn with multiple worker processes
CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:5000", "app:app"]
