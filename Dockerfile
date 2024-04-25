# Use an official Python runtime as a base image
FROM python:3.10-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Install system dependencies for general use and audio handling
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus0 \
    python3-dev \
    libasound2-dev \
&& rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["python", "bot.py"]
