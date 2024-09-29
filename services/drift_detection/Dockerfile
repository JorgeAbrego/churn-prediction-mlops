FROM python:3.10.14-slim-bullseye

WORKDIR /app

COPY . .

RUN apt-get update \
  && apt-get dist-upgrade -y \
  && apt-get install -y --no-install-recommends \
    python3-dev \
    libpq-dev \
  && apt-get clean \
  && rm -rf \
    /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/* \
  && pip install --no-cache-dir -r requirements.txt 

CMD ["python", "./main.py"]