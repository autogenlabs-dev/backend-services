# Use a slim Python base image for smaller size
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
# This step is cached if requirements.txt doesn't change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your FastAPI application will listen on
EXPOSE 8000


# Run the application
CMD ["uvicorn", "minimal_auth_server:app", "--host", "0.0.0.0", "--port", "8000"]
