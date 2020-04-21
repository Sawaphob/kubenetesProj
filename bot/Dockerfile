FROM python

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5003
CMD ["python", "main.py"]
