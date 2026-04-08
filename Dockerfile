FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire project (including engine/)
COPY . /app

# Set the environment to the project root
ENV PYTHONPATH="/app"

# Run the server from the server directory
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7860"]