FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update \
    && apt-get install -y build-essential \
                          default-libmysqlclient-dev \
                          libssl-dev \
                          libffi-dev \
                          libmariadb-dev-compat \
                          libmariadb-dev \
    && apt-get clean

# Create and set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/
