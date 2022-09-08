# leverage the renci python base image
FROM renciorg/renci-python-image:v0.0.1
RUN python -m pip install --upgrade pip
WORKDIR /code
COPY ./requirements*.txt /code/
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements-service.txt
COPY ./translator /code/translator
COPY ./tests /code/tests
COPY ./app /code/app
# allow non root user write access to tests dir
RUN chown nru:nru /code/tests
# use non root user
USER nru
# change port to allowed port
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8080"]
