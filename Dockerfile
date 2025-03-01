# Dockerfile
FROM python:3-alpine

RUN apk add --no-cache tzdata

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Create the logs directory
RUN mkdir -p {logs,config}

# Set the entry point
ENTRYPOINT ["python", "-u", "main.py"]