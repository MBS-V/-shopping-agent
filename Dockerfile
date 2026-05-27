# Dockerfile
# Tells Docker how to package your app into a container.
# A container is a lightweight box that has everything 
# needed to run your app — Python, packages, code.

# Start from official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (Docker caches this layer)
# If requirements don't change, this layer is reused
COPY requirements.txt .

# Install all packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port 8080 (Cloud Run requires this)
EXPOSE 8080

# Command to run when container starts
CMD ["streamlit", "run", "app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]