FROM python:3.11
WORKDIR /bot
COPY requirements.txt /bot/
RUN python3 -m venv venv
RUN source venv/bin/activate
RUN venv/bin/pip install --upgrade google-cloud
RUN pip install -r requirements.txt
COPY . /bot
CMD python main.py