FROM  continuumio/miniconda3

COPY . .

#---------------- Prepare the envirennment
RUN conda env update --name base --file environment.yaml --prune
SHELL ["conda", "run", "--name", "base", "/bin/bash", "-c"]

EXPOSE 5000

ENTRYPOINT ["conda", "run", "--name", "base", "python", "src/app.py"]