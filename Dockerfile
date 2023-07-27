FROM alpine:3.17
# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN mkdir -p /opt/usermanager
WORKDIR /opt
COPY . .
RUN pip3 install -r ./requirements.txt
RUN chmod +x ./start-app.sh
ENTRYPOINT [ "sh", "start-app.sh" ]