FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    opensc \
    openssl \
    libengine-pkcs11-openssl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

# Copy the libeTPkcs11.so driver
COPY libeTPkcs11.so /usr/lib64/libeTPkcs11.so

ENV OPENSSL_CONF=/app/openssl.cnf

CMD ["python3", "app.py"]