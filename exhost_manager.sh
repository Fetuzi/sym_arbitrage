#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <exchange_name> {start|stop|status}"
    exit 1
fi

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export PYTHONPATH=$DIR
EXCHANGE_NAME=$1
LOG_FILE="$DIR/log/${EXCHANGE_NAME}_rest_manager.log"

# Ensure log directory exists
mkdir -p "$DIR/log/"

start_app() {
    if pgrep -f "uvicorn rest_manager:app" > /dev/null; then
        echo "FastAPI app for ${EXCHANGE_NAME} seems to be already running. Stop it first."
        exit 1
    fi
    cd "$DIR/exhost/${EXCHANGE_NAME}/" || { echo "Directory exhost/${EXCHANGE_NAME}/ does not exist"; exit 1; }
    echo "Starting FastAPI app for ${EXCHANGE_NAME}..."
    nohup uvicorn rest_manager:app --reload > $LOG_FILE 2>&1 &
    cd - > /dev/null
    echo "FastAPI app for ${EXCHANGE_NAME} started and logging to $LOG_FILE"
}

stop_app() {
    if pgrep -f "uvicorn rest_manager:app" > /dev/null; then
        echo "Stopping FastAPI app for ${EXCHANGE_NAME}..."
        pkill -f "uvicorn rest_manager:app"
        echo "FastAPI app for ${EXCHANGE_NAME} stopped."
    else
        echo "No FastAPI app for ${EXCHANGE_NAME} is running."
    fi
}

check_status() {
    if pgrep -f "uvicorn rest_manager:app" > /dev/null; then
        echo "FastAPI app for ${EXCHANGE_NAME} is running."
    else
        echo "FastAPI app for ${EXCHANGE_NAME} is not running."
    fi
}

case $2 in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 <exchange_name> {start|stop|status}"
        ;;
esac
