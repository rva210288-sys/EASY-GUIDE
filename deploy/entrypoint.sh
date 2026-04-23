#!/bin/bash

pip install -r requirements.txt
npm install

python manage.py migrate
./node_modules/.bin/webpack
echo "yes" | python manage.py collectstatic

exec "$@"
