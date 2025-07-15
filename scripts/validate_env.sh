#!/bin/bash

# Validate required environment variables for Matomo and MySQL
required_vars=("MATOMO_USER" "MATOMO_PASSWORD" "MYSQL_ROOT_PASSWORD")

missing_vars=()

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    missing_vars+=("$var")
  fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
  echo "Error: The following environment variables are missing: ${missing_vars[*]}"
  echo "Please ensure you use the '--env-file' option with docker-compose to provide these variables."
  exit 1
fi

echo "All required environment variables are set."
