FROM python:3.12-slim-bookworm
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers PYTHONDONTWRITEBYTECODE=1
RUN pip install --no-cache-dir playwright==1.65.2 && python -m playwright install --with-deps chromium && useradd --create-home --uid 1000 worker && chmod -R a+rX /opt/pw-browsers
WORKDIR /app
COPY browser_worker_protocol_v1.py render.py render_entry.py service.py /app/
USER 1000
EXPOSE 7860
CMD ["python","/app/service.py"]
