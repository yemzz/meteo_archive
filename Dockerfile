FROM python:3.6-stretch

# basics
WORKDIR  /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

COPY /entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN apt-get update && apt-get install -y \
  gcc \
  gfortran \
  g++ \
  build-essential \
  libgrib-api-dev

RUN pip install numpy pyproj

RUN git clone https://github.com/jswhit/pygrib.git pygrib && \
  cd pygrib && git checkout tags/v2.0.2rel

COPY setup.cfg ./pygrib/setup.cfg

RUN cd pygrib && python setup.py build && python setup.py install

CMD ["python"]

COPY docker/python .

ENTRYPOINT ["/entrypoint.sh"]

#Execute this when rvm not found: source /etc/profile.d/rvm.sh