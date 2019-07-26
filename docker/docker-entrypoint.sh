#!/bin/sh
set -e

if [ "$1" = 'bash' ]; then
  cms admin mongo start
fi

exec "$@"
