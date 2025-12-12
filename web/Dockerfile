FROM python:3.12-slim

ARG HOSTNAME
ENV HOSTNAME=${HOSTNAME}

WORKDIR /home

COPY web.py /home/web.py

# Installa le dipendenze
RUN pip install --no-cache-dir flask requests

# Espone la porta usata dalla web app
EXPOSE 8080

CMD ["python", "web.py"]
