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
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_web.txt .

# Upgrade pip and install wheel for better compatibility
RUN pip install --upgrade pip setuptools wheel

# Install numpy first to avoid compatibility issues
RUN pip install --no-cache-dir numpy==1.24.3

# Install pandas next
RUN pip install --no-cache-dir pandas==1.5.3

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements_web.txt

# Copy application files
COPY app.py .
COPY ocr_processor.py .
COPY templates/ ./templates/

# Create uploads directory
RUN mkdir -p /tmp/uploads

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]