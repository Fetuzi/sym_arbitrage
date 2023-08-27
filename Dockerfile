# Use an official Python runtime as the parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY ./requirements.txt /app/requirements.txt

# Install necessary packages and any dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Set the command to run your application using uvicorn
# Replace `exhost.binancefuture.rest_manager:app` with your specific module path and FastAPI app instance
ENTRYPOINT ["python"]