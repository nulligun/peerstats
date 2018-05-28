#!/bin/bash

cd /var/www/peerstats
/usr/bin/gunicorn3 -b 127.0.0.1:8115 peerstats:app
