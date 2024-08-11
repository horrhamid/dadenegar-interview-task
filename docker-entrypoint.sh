#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset
/bin/bash scripts/local-remigrate.sh
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
