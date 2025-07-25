# syntax=docker/dockerfile:1
FROM docker.io/continuumio/miniconda3:latest

WORKDIR /

COPY ./requirements.txt /src/requirements.txt

# Install required system packages (added ffmpeg here)
RUN apt-get update && apt-get install -y runit gcc ffmpeg

# Create conda environment and install dependencies
RUN conda create -n promptflow-serve python=3.9.16 pip=23.0.1 -q -y && \
    conda run -n promptflow-serve \
    pip install -r /src/requirements.txt && \
    conda run -n promptflow-serve pip install promptflow && \
    conda run -n promptflow-serve pip install keyrings.alt && \
    conda run -n promptflow-serve pip install gunicorn==22.0.0 && \
    conda run -n promptflow-serve pip install 'uvicorn>=0.27.0,<1.0.0' && \
    conda run -n promptflow-serve pip cache purge && \
    conda clean -a -y

COPY ./src /src

EXPOSE 8080

# Reset runsvdir
RUN rm -rf /var/runit
COPY ./runit /var/runit
RUN chmod -R +x /var/runit

COPY ./start.sh /
CMD ["bash", "./start.sh"]
