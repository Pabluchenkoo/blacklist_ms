# Usar la imagen oficial de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de requerimientos y luego instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el contenido del proyecto al contenedor
COPY . .

# Exponer el puerto donde correrá la aplicación FastAPI
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]

#configuracion new relic
RUN pip install newrelic
ENV NEW_RELIC_APP_NAME="blacklist"
ENV NEW_RELIC_LOG=stdout
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true
ENV NEW_RELIC_LICENSE_KEY=eed6e6bf6ad841d69fc97e8fa6488bb7FFFFNRAL
ENV NEW_RELIC_LOG_LEVEL=info
ENTRYPOINT [ "newrelic-admin", "run-program" ]