#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/server_cpp"

mkdir -p build
cd build

if [ ! -f "CMakeCache.txt" ]; then
    cmake ..
fi

cmake --build . --config Release

if [ -f "bin/voting_server" ]; then
    ./bin/voting_server
elif [ -f "voting_server" ]; then
    ./voting_server
else
    echo "voting_server executable not found"
    exit 1
fi