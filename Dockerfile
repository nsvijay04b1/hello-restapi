FROM tiangolo/uwsgi-nginx:python2.7
LABEL maintainer="Vijay <nsvijay04b1@gmail.com>"
RUN pip install flask psycopg2 six requests gunicorn 
#RUN pip install flask psycopg2 six requests --proxy http://10.XX.XX.70:8080  for proxy envs
#ENV HTTP_PROXY http://10.XX.XX.70:8080
#ENV HTTPS_PROXY http://10.XX.XX.70:8080
#ENV NO_PROXY localhost
ENV STATIC_URL /static
# Absolute path in where the static files wil be
ENV STATIC_PATH /app/static

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
ENV STATIC_INDEX 0

# Add demo app
COPY ./app /app
WORKDIR /app

# Make /app/* available to be imported by Python globally to better support several use cases like Alembic migrations.
ENV PYTHONPATH=/app

# Move the base entrypoint to reuse it
RUN mv /entrypoint.sh /uwsgi-nginx-entrypoint.sh
# Copy the entrypoint that will generate Nginx additional configs
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# It will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Supervisor, which in turn will start Nginx and uWSGI
CMD ["/start.sh"]
