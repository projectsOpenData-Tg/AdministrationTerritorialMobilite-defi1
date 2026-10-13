# syntax=docker/dockerfile:1
# Image du tableau de bord « Mobilité et sécurité routière au Togo » (Défi 1).
#
# Le contexte de build est la RACINE du dépôt (pas dashboard/), car l'application lit
# ../data par rapport à dashboard/ (voir donnees.py). Construire avec :
#     docker build -f dashboard/Dockerfile -t togo-dashboard .
#
# On ne copie que le code de l'app et les SEULES données que le tableau de bord lit
# (analysis, processed, reference, et data/raw/_SOURCES.csv pour la page Méthodologie) :
# pas de données brutes lourdes ni de rapports de profilage.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 1) Dépendances d'abord : cette couche reste en cache tant que requirements.txt ne change pas.
COPY dashboard/requirements.txt dashboard/requirements.txt
RUN pip install -r dashboard/requirements.txt

# 2) Code de l'application (dont .streamlit/config.toml et static/).
COPY dashboard/ dashboard/

# 3) Données lues par le tableau de bord (chacune à côté de dashboard/, comme dans le dépôt).
COPY data/analysis/        data/analysis/
COPY data/processed/       data/processed/
COPY data/reference/       data/reference/
COPY data/raw/_SOURCES.csv data/raw/_SOURCES.csv

EXPOSE 8501

# On démarre DEPUIS dashboard/ : .streamlit/config.toml et static/ sont alors résolus
# comme en local, et donnees.py trouve ../data (= /app/data).
WORKDIR /app/dashboard

# Sonde de disponibilité : l'endpoint de santé interne de Streamlit renvoie « ok ».
HEALTHCHECK --interval=15s --timeout=5s --start-period=40s --retries=10 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health',timeout=4).read()==b'ok' else 1)"

CMD ["streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", "--server.port=8501", \
     "--server.headless=true", "--browser.gatherUsageStats=false"]
