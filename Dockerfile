# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
# This includes app.py and any other necessary files/directories
COPY . .

# Expose port 8000 to allow communication to the application
# FastAPI/Uvicorn default port is 8000
EXPOSE 8000

# Run app.py when the container launches using uvicorn
# 'app:app' refers to the 'app' instance created in the 'app.py' file
# '--host 0.0.0.0' makes the server accessible from outside the container
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

