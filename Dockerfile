FROM python:3.9.13
WORKDIR /app
ADD Good_Day.py .
ADD requirements.txt .
ADD .env .
RUN pip install -r requirements.txt
CMD ["python", "./Good_Day.py"]