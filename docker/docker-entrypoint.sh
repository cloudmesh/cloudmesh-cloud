#!/bin/sh
set -e

cms admin mongo start

exec "$@"
