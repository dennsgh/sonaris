#!/bin/sh
touch .env
echo Setting up environment with OS type: $OSTYPE

if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
    export CONFIG=$(dirname "$SCRIPT")
    export WORKINGDIR=$(dirname "$CONFIG")
elif [[ "$OSTYPE" == "darwin"* ]]; then
    SCRIPT="$( cd "$( dirname "$0" )" && pwd )"
    export WORKINGDIR=$(dirname "$SCRIPT")
    export CONFIG="$WORKINGDIR/etc"
fi

export DATA="$WORKINGDIR/data"

export FRONTEND_SRC="$WORKINGDIR/frontend/src"
export SRC="$WORKINGDIR/src"

if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    export PYTHONPATH="$FRONTEND_SRC:$SRC"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
    export PYTHONPATH="$FRONTEND_SRC:$SRC"
else
    export PYTHONPATH="$PYTHONPATH:$WORKINGDIR/src:$WORKINGDIR/frontend/src"
fi
# Determine which dotenv to use
if gem list dotenv -i > /dev/null 2>&1; then
    # If Ruby dotenv exists, use Python dotenv explicitly
    dotenv_command="/usr/bin/dotenv" # Replace this with your actual python dotenv command if different
else
    dotenv_command="dotenv" # Assuming this defaults to the correct dotenv
fi

# Now use the chosen dotenv command
$dotenv_command -f "$WORKINGDIR/.env" set WORKINGDIR "$WORKINGDIR"
$dotenv_command -f "$WORKINGDIR/.env" set CONFIG "$CONFIG"
$dotenv_command -f "$WORKINGDIR/.env" set DATA "$DATA"
$dotenv_command -f "$WORKINGDIR/.env" set PYTHONPATH "$PYTHONPATH"