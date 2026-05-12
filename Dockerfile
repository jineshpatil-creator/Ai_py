# Use the official Microsoft Playwright image with Python pre-installed
# This guarantees all OS-level browser dependencies are present.
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the framework files into the container
COPY . .

# Set environment variables (API Key should be passed at runtime, not baked in)
ENV GEMINI_API_KEY=""

# The default command to run when the container starts
CMD ["python", "-m", "pytest"]
