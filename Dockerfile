FROM python:3.11-slim

LABEL maintainer="FVN"

ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 LC_ALL=C.UTF-8


# (Opcional) dependências mínimas de compilação; remova se não precisar
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Instale dependências Python (wheels leves)
RUN pip install --upgrade pip setuptools wheel && \
    pip install \
      numpy \
      pandas \
      shapely>=2 \
      pyproj>=3.6 \
      pyogrio>=0.9 \
      geopandas>=0.14 \
      plotly \
      pdfplumber \
      openpyxl

# Estrutura esperada (paths.py)
RUN mkdir -p data/raw data/processed docs

# Copie o projeto (use .dockerignore para não levar data/)
COPY . /workspace

CMD ["bash"]