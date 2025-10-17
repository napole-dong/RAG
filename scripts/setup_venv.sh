#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/setup_venv.sh [venv-name]
VENV_NAME=${1:-.venv}
PYTHON=${PYTHON:-python}

echo "Creating virtual environment '${VENV_NAME}' using ${PYTHON}"
${PYTHON} -m venv "${VENV_NAME}"

OSNAME=$(uname -s 2>/dev/null || echo unknown)
if [[ "$OSNAME" == MINGW* || "$OSNAME" == MSYS* || "$OSNAME" == CYGWIN* ]]; then
	# Git Bash on Windows
	ACTIVATE_CMD="source ${VENV_NAME}/Scripts/activate"
	PIP_CMD="${VENV_NAME}/Scripts/pip"
else
	ACTIVATE_CMD="source ${VENV_NAME}/bin/activate"
	PIP_CMD="${VENV_NAME}/bin/pip"
fi

echo "To activate the virtualenv after creation run:"
echo "  $ACTIVATE_CMD"

echo "Upgrading pip"
"$PIP_CMD" install --upgrade pip setuptools wheel
echo "Installing requirements.txt"
"$PIP_CMD" install -r requirements.txt
echo "Setup complete. Activate with: $ACTIVATE_CMD"
