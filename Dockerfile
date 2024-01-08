FROM python:3.10.12

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#ENV FLASK_APP run.py
ENV DEBUG False

COPY requirements.txt .

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# install nano editor
# RUN apt-get update && apt-get install -y nano && apt clean && apt-get clean

COPY . .

COPY production.env .env

# RUN flask db init
# RUN flask db migrate
#RUN flask db upgrade

# gunicorn
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "run:app"]
