FROM python:3.7-slim

WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install exact compatible versions
RUN pip install --no-cache-dir \
    absl-py==0.15.0 \
    numpy==1.19.5 \
    six==1.16.0 \
    sympy==1.4

# Clone repository
RUN git clone https://github.com/google-deepmind/mathematics_dataset.git

WORKDIR /app/mathematics_dataset

# Install in editable mode
RUN pip install -e .

# Copy custom generation script
COPY custom_generate_by_difficulty.py /app/mathematics_dataset/mathematics_dataset/

# Set working directory back to app root
WORKDIR /app

# Default command opens a bash shell
CMD ["/bin/bash"]
