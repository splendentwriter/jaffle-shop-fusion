#!/bin/sh
set -e

case "$1" in
  deps)
    dbt deps
    ;;
  seed)
    dbt seed --vars '{load_source_data: true}'
    ;;
  snapshot)
    dbt snapshot
    ;;
  build)
    # exclude seeds: raw tables are now kept fresh by the streaming generator
    # (scripts/generate_stream_data.py), not by re-loading the static CSVs
    dbt build --exclude resource_type:seed
    ;;
  test)
    dbt test
    ;;
  *)
    echo "Unknown step: $1" >&2
    exit 1
    ;;
esac
