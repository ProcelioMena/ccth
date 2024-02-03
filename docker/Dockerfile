FROM python:3.11-slim-bullseye as python

ARG APP_HOME=/app
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential \
  libpq-dev \
  gettext \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN addgroup --system apiuser && adduser --system --ingroup apiuser apiuser

COPY --chown=apiuser:apiuser ./src/ ${APP_HOME}
WORKDIR ${APP_HOME}

COPY --chown=apiuser:apiuser docker/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

RUN chown apiuser:apiuser ${APP_HOME}
USER apiuser
ENTRYPOINT ["/entrypoint"]
