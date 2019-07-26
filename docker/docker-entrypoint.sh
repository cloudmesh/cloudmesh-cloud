#!/bin/sh
set -e

if [ "$1" = 'bash' ]; then
  echo
  echo "START MONGO"
  echo
  cms admin mongo start
fi

exec "$@"
