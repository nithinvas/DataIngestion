# Use the official Python image.
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && pip install flask google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib PyPDF2 bs4

# Expose port 8080
EXPOSE 8080

# Run the Flask app
CMD ["python", "main.py"]
