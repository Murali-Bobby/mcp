# Use an official Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Install the package in editable mode
RUN pip install -e .

# Set environment variables (optional if using .env at runtime)
# ENV VAR_NAME=value

# Expose the port
EXPOSE 8080
# Run the app
CMD ["python", "main.py"]
