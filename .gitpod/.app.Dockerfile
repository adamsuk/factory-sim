FROM  sra405/flask-boilerplate

COPY ./src/ .

EXPOSE 5000

ENTRYPOINT ["python", "app.py"]
