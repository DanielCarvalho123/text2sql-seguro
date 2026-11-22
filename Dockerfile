FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY eval/ eval/

# Gera o banco de demonstração (determinístico, semente 42)
RUN python -m text2sql.dados data/loja.db

# Usuário sem privilégios de administrador
RUN useradd --create-home app && mkdir -p logs eval/resultados && chown -R app:app /app
USER app

EXPOSE 8501
CMD ["streamlit", "run", "src/app.py", "--server.address=0.0.0.0", "--server.port=8501", \
     "--browser.gatherUsageStats=false"]
