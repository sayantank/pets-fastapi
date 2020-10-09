FROM fastdotai/fastai:latest

COPY requirements.txt .

RUN pip install --upgrade -r requirements.txt

COPY . .

RUN adduser myuser
USER myuser

CMD uvicorn main:app --host 127.0.0.1 --port 8000