FROM python:3.12-slim

WORKDIR /app

RUN python3 -m pip install --pre dbt

COPY . .

RUN dbt deps

ENTRYPOINT ["dbt"]
CMD ["build"]
