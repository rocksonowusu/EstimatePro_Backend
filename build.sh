#!/usr/bin/env bash
apt-get update && apt-get install -y \
  build-essential \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libcairo2 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  libssl-dev \
  python3-dev \
  libjpeg-dev \
  zlib1g-dev

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
