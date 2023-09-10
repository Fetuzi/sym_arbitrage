#!/bin/bash

# Function to SSH into a server and run git pull in a specific directory
run_git_pull() {
  local server=$1
  local dir=$2
  ssh $server "cd $dir && git pull"
}

# Function to SSH into a server and run docker compose commands
run_docker_command() {
  local server=$1
  local dir=$2
  local docker_file=$3
  local command=$4
  ssh $server "cd $dir && docker compose -f $docker_file $command"
}

# Function to copy logs from a server to a local directory
copy_logs() {
  local server=$1
  local remote_dir=$2
  local local_dir=$3
  rsync -av --append "$server:$remote_dir/*" "$local_dir"
}

# Function to clear logs on a server
clear_logs() {
  local server=$1
  local dir=$2
  ssh $server "cd $dir/log && rm -f *"
}

# Function to sync a local file to a remote directory on a server
sync_file() {
  local file=$1
  local server=$2
  local remote_dir=$3
  scp "$file" "$server:$remote_dir"
}

# Create log directories if they don't exist
mkdir -p log/tokyo_log
mkdir -p log/hk_log


# Check command argument
case "$1" in
  pull)
    # Run git pull on tokyo008-free
    run_git_pull "tokyo008-free" "sym_arbitrage"

    # Run git pull on hk008-free
    run_git_pull "hk008-free" "sym_arbitrage"
    ;;
  up)
    # Run docker-compose up on tokyo008-free
    run_docker_command "tokyo008-free" "sym_arbitrage" "docker-compose.tokyo.yaml" "up -d"

    # Run docker-compose up on hk008-free
    run_docker_command "hk008-free" "sym_arbitrage" "docker-compose.hk.yaml" "up -d"
    ;;
  down)
    # Run docker-compose down on tokyo008-free
    run_docker_command "tokyo008-free" "sym_arbitrage" "docker-compose.tokyo.yaml" "down"

    # Run docker-compose down on hk008-free
    run_docker_command "hk008-free" "sym_arbitrage" "docker-compose.hk.yaml" "down"
    ;;
  build)
    # Run docker-compose build on tokyo008-free
    run_docker_command "tokyo008-free" "sym_arbitrage" "docker-compose.tokyo.yaml" "build"

    # Run docker-compose build on hk008-free
    run_docker_command "hk008-free" "sym_arbitrage" "docker-compose.hk.yaml" "build"
    ;;
  ps)
    # Run docker-compose build on tokyo008-free
    run_docker_command "tokyo008-free" "sym_arbitrage" "docker-compose.tokyo.yaml" "ps"

    # Run docker-compose build on hk008-free
    run_docker_command "hk008-free" "sym_arbitrage" "docker-compose.hk.yaml" "ps"
    ;;
  log)
    copy_logs "tokyo008-free" "~/sym_arbitrage/log" "log/tokyo_log"
    copy_logs "hk008-free" "~/sym_arbitrage/log" "log/hk_log"
    ;;
  clear)
    clear_logs "tokyo008-free" "~/sym_arbitrage"
    clear_logs "hk008-free" "~/sym_arbitrage"
    ;;
  sync)
    sync_file "./config/binancefuture_okx_arb.py" "tokyo008-free" "~/sym_arbitrage/config/binancefuture_okx_arb.py"
    sync_file "./config/binancefuture_okx_arb.py" "hk008-free" "~/sym_arbitrage/config/binancefuture_okx_arb.py"
    ;;
  *)
    echo "Invalid command. Usage: ./remote.sh pull|up|down|build|ps|log|clear|sync"
    ;;
esac
