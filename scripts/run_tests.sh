#!/bin/bash

# Create reports directory if it doesn't exist
mkdir -p reports

# Run pytest with reporting options
pytest "$@" --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html
