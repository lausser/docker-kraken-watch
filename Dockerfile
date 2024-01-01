FROM python:3.12.1
LABEL org.opencontainers.image.authors="Gerhard Lausser"
LABEL description="Watch Kraken transactions"

ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y tini
RUN pip install requests

ADD kraken.py /root
RUN chmod 755 /root/kraken.py
ADD VERSION /root
CMD ["/usr/bin/tini", "-s", "python", "/root/kraken.py"]
