FROM python:3.7
LABEL Artem Chernyshev 'dtenebrae@gmail.com'

RUN mkdir /home/project
COPY . /home/project/

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

RUN rm /home/project/requirements.txt
RUN rm /home/project/docker-entrypoint.sh
RUN rm /home/project/README.md
RUN rm -rf /home/project/env

EXPOSE 5000

COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

WORKDIR /home/project
ENTRYPOINT ["/docker-entrypoint.sh"]
