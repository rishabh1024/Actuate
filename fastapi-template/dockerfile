# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /URLShortener

# Copy the requirements files into the container
COPY requirements.txt /URLShortener/requirements.txt
COPY dev-requirements.txt /URLShortener/dev-requirements.txt

# Install the required Python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /URLShortener/requirements.txt
RUN pip install --no-cache-dir -r /URLShortener/dev-requirements.txt

# Copy the application code into the container
COPY . /URLShortener

# Expose the port on which the FastAPI application will run
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]