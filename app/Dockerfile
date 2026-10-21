FROM python:3.11-slim
RUN groupadd -g 1001 appgroup && useradd -u 1001 -g appgroup -s /bin/sh -m appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chown -R appuser:appgroup /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
