FROM mcr.microsoft.com/azure-functions/python:4-python3.10

# 0. Install essential packages
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# 1. Install Poppler to transform pdfs to images
RUN apt-get update && apt-get -y install poppler-utils && apt-get clean

# 2. Install Tesseract
RUN apt-get update && apt install tesseract-ocr-por -y

# 3. copy python code to image
COPY . /home/site/wwwroot

# 4. Install other packages
RUN cd /home/site/wwwroot && \
    pip install -r requirements.txt
