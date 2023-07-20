FROM python:3.10.12
RUN mkdir /app
WORKDIR app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN chmod a+x docker_start_app/*.sh