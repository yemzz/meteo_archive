FROM python:3.7

# basics
WORKDIR  /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

COPY /docker/python/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY . .

ENTRYPOINT ["/entrypoint.sh"]

#Execute this when rvm not found: source /etc/profile.d/rvm.sh