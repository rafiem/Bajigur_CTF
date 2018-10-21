FROM python:2.7

COPY . /home/bajigur_ctf
WORKDIR /home/bajigur_ctf

EXPOSE 5000
EXPOSE YOUR_PORT

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install mysql-client -y
RUN apt-get install python-pip -y
RUN pip install --upgrade pip
RUN pip install Flask
RUN pip install passlib 
RUN pip install flask-mysql
RUN pip install flask-mysqldb
RUN pip install WTForms

CMD ["python","serve.py"]
