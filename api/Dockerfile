# Python 3.11.8 image
FROM pytorch/pytorch:2.5.0-cuda12.4-cudnn9-runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    MKL_THREADING_LAYER=GNU \
    OMP_NUM_THREADS=1 

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc git zip unzip wget curl htop libgl1 libglib2.0-0 libpython3-dev gnupg \
        g++ libusb-1.0-0 libsm6 openssl tar \
    && rm -rf /var/lib/apt/lists/* 
COPY . /app
WORKDIR /app
RUN pip install -r requirements/requirements.txt
CMD ["python", "src/image_model_server/app.py"]
