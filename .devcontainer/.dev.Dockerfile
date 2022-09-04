FROM gitpod/workspace-base:latest

USER root
# Install util tools.
RUN apt-get update \
 && apt-get install -y \
  apt-utils \
  sudo \
  git \
  less \
  wget

RUN mkdir -p /workspace/data \
    && chown -R gitpod:gitpod /workspace/data
  
RUN mkdir /home/gitpod/.conda
# Install conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc
    
RUN chown -R gitpod:gitpod /opt/conda \
    && chmod -R 777 /opt/conda \
    && chown -R gitpod:gitpod /home/gitpod/.conda \
    && chmod -R 777 /home/gitpod/.conda

## ADD CONDA PATH TO LINUX PATH 
ENV PATH /opt/conda/bin:$PATH

COPY environment.yaml environment.yaml

# make conda environment
RUN conda env create --file environment.yaml --name dev_env

## Link to new python env
RUN ln -s /opt/conda/envs/dev_env/bin/python /usr/bin/python

# Give back control
USER root

# Cleaning
RUN apt-get clean

SHELL ["conda", "run", "--no-capture-output", "-n", "dev_env", "/bin/bash", "-c"]
# activate
RUN echo "source activate dev_env" > ~/.bashrc
# RUN conda activate dev_env
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "dev_env", "/bin/bash", "-c"]
