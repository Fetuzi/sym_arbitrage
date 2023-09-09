#!/bin/bash

# Function to set environment variables for development
set_mac_env() {
  export PYTHONPATH="/Users/yite/Projects/sym_arbitrage"
  export DEPLOYMENT="MAC"
  echo "Development environment variables set."
}

# Function to set environment variables for tokyo production
set_tokyo_env() {
  export PYTHONPATH="/home/ubuntu/sym_arbitrage"
  export DEPLOYMENT="TOKYO"
  echo "Tokyo environment variables set."
}

# Function to set environment variables for tokyo production
set_hk_env() {
  export PYTHONPATH="/home/ubuntu/sym_arbitrage"
  export DEPLOYMENT="HK"
  echo "HK environment variables set."
}

# Main script execution
if [ -z "$1" ]; then
  echo "Please provide an environment (mac/tokyo/hk)."
  exit 1
fi

case $1 in
  "mac")
    set_mac_env
    ;;
  "tokyo")
    set_tokyo_env
    ;;
  "hk")
    set_hk_env
    ;;
  *)
    echo "Invalid environment specified. Use development/staging/production."
    exit 1
    ;;
esac
