# Build an egg of your project.

FROM python:3.12-slim AS build-stage

RUN pip install --no-cache-dir scrapyd-client

WORKDIR /workdir

COPY . .

RUN scrapyd-deploy --build-egg=gmaps_screenshot_engine.egg

# Build the image.

FROM python:3.12-slim

# Install Scrapy dependencies - and any others for your project.

RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libimagequant-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_NO_DEV=1
ENV PATH="/.venv/bin:$PATH"
ENV UV_HTTP_TIMEOUT=3600

# Mount two volumes for configuration and runtime.

VOLUME /etc/scrapyd/ /var/lib/scrapyd/

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

RUN playwright install firefox --with-deps

COPY ./scrapyd.conf /etc/scrapyd/

RUN mkdir -p /src/eggs/gmaps_screenshot_engine

COPY --from=build-stage /workdir/gmaps_screenshot_engine.egg /src/eggs/gmaps_screenshot_engine/1.egg

EXPOSE 6800

ENTRYPOINT ["scrapyd", "--pidfile="]
