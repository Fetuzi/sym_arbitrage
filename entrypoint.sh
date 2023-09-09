#!/bin/bash
source /app/env.sh $1
shift
exec "$@"
