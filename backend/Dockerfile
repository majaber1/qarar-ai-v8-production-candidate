FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN addgroup --system qarar && adduser --system --ingroup qarar qarar && chown -R qarar:qarar /app
USER qarar
CMD ["python","-m","uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
