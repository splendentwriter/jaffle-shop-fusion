FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --pre dbt

COPY . .

RUN dbt deps

ENTRYPOINT ["dbt"]
CMD ["build"]
