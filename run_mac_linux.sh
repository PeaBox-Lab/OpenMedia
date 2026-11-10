#!/bin/sh
python3 -m http.server 8080 &
echo "Open http://localhost:8080"
wait
