#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Install tailwind dependencies
python manage.py tailwind install

# Build tailwind
python manage.py tailwind build

# Collect static files
python manage.py collectstatic --no-input

# Apply migrations
python manage.py migrate