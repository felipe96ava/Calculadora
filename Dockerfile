FROM python:3.11-slim

WORKDIR /app

# instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar código
COPY . .

# porta usada pelo Fly
ENV PORT=8080
EXPOSE 8080

# iniciar aplicação
CMD ["python", "main.py"]