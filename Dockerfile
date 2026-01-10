# Build an egg of your project.

FROM python AS build-stage

RUN pip install --no-cache-dir scrapyd-client

WORKDIR /workdir

COPY . .

RUN scrapyd-deploy --build-egg=gmaps_screenshot_engine.egg

# Build the image.

FROM python:alpine

# Install Scrapy dependencies - and any others for your project.

RUN apk --no-cache add --virtual build-dependencies \
    gcc \
    musl-dev \
    libffi-dev \
    libressl-dev \
    libxml2-dev \
    libxslt-dev \
    && apk del build-dependencies \
    && apk add \
    libressl \
    libxml2 \
    libxslt

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_NO_DEV=1
ENV PATH="/.venv/bin:$PATH"

# Mount two volumes for configuration and runtime.

VOLUME /etc/scrapyd/ /var/lib/scrapyd/

COPY ./scrapyd.conf /etc/scrapyd/

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

RUN mkdir -p /src/eggs/gmaps_screenshot_engine

COPY --from=build-stage /workdir/gmaps_screenshot_engine.egg /src/eggs/gmaps_screenshot_engine/1.egg

EXPOSE 6800

ENTRYPOINT ["scrapyd", "--pidfile="]
