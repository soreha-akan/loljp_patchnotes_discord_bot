FROM python:3.13-slim
WORKDIR /bot
COPY requirements.txt /bot/
RUN pip install -r requirements.txt
COPY . /bot
ENV PYTHONPATH=/bot
CMD python app/main.py