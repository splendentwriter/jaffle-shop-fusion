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
    dbt build
    ;;
  test)
    dbt test
    ;;
  *)
    echo "Unknown step: $1" >&2
    exit 1
    ;;
esac
