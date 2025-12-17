FROM python:3.11-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app


RUN apt-get update && apt-get install -y \
libpq-dev \
gcc \
netcat-traditional \
gdal-bin \
binutils \
libproj-dev \
&& rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY waitfordb.py .
# Copy entrypoint to /usr/local/bin to avoid being overwritten by volume mount
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

COPY . .


# Fix windows line endings if any, and make executable
RUN sed -i 's/\r$//g' /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]