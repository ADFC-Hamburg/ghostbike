#!/bin/bash
VENV_DIR=".venv"
python3 -m venv $VENV_DIR

$VENV_DIR/bin/pip install --upgrade pip
$VENV_DIR/bin/pip install -r requirements.txt
