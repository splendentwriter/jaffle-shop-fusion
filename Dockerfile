FROM golang:1.23-alpine AS runner-build
WORKDIR /src
COPY runner/ .
RUN CGO_ENABLED=0 GOOS=linux go build -o /runner .

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --pre dbt

COPY . .
COPY --from=runner-build /runner /usr/local/bin/runner
COPY docker/profiles.yml /root/.dbt/profiles.yml

ENTRYPOINT ["runner"]
