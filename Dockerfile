FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3308

CMD sh -c "flask db upgrade && python -m app.seed && gunicorn -b 0.0.0.0:${PORT:-3308} 'app:create_app()'"
