# Builder stage
FROM python:3.10-slim-buster as builder

# Set the working directory in the builder stage
WORKDIR /build

# Install system dependencies required for building your application
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libopus0 \
    python3-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy your application files and install Python dependencies
COPY . /build
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.10-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Install runtime dependencies (if any)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the necessary artifacts from the builder stage
COPY --from=builder /build /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["python", "bot.py"]