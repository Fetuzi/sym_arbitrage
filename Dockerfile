# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install networking tools and vim
RUN apt-get update \
    && apt-get install -y netcat-openbsd iputils-ping curl vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Run app.py when the container launches
ENTRYPOINT ["./entrypoint.sh"]

