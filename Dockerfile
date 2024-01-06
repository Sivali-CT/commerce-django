FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r requirements.txt && \
    chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]