FROM python:3.8

#working directory
WORKDIR /usr/src/app

#Copy contents into the container
COPY bitcoin_app.py /app/bitcoin_app.py

#Install the needed packages
RUN pip install Flask datetime pytz Flask-SQLAlchemy requests APScheduler SQLAlchemy

#open port
EXPOSE 80

#Define environment variable
#ENV FLASK_APP=app.py

# Run app.py 
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
