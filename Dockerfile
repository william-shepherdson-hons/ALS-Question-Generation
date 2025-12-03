FROM python:3.7-slim

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install required Python packages (Python 3.7 compatible versions)
RUN pip install --no-cache-dir \
    absl-py==0.15.0 \
    numpy==1.19.5 \
    six==1.16.0 \
    sympy==1.4 \
    fastapi==0.103.2 \
    uvicorn==0.22.0

# Clone Google's mathematics dataset
RUN git clone https://github.com/google-deepmind/mathematics_dataset.git

WORKDIR /app/mathematics_dataset

# Install dataset package in editable mode
RUN pip install -e .

# Copy your custom generator script into the module
COPY custom_generate_by_difficulty.py /app/mathematics_dataset/mathematics_dataset/

# Copy the FastAPI wrapper
COPY api.py /app/api.py

WORKDIR /app

EXPOSE 5000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5000"]
