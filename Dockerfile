FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ghostscript \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_web.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_web.txt

# Copy application files
COPY app.py .
COPY templates/ ./templates/

# Create uploads directory
RUN mkdir -p /tmp/uploads

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]