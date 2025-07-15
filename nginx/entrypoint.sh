#!/bin/bash

# Load all *.so modules from modules folder
for mod in /usr/lib/nginx/modules/*.so; do
    echo "load_module \"$mod\";" >> /etc/nginx/modules-enabled/dynamic.conf
done

exec nginx -g "daemon off;"

