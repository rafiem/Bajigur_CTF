FROM mysql:5.7

EXPOSE 3306

RUN apt-get update -y && apt-get upgrade -y
RUN cp /usr/share/zoneinfo/Asia/Jakarta /etc/localtime
RUN apt-get install nano
CMD ["service mysql start"]
