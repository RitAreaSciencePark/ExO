#!/bin/bash

# Fix ownership/permissions on mounted volume
echo "[entrypoint] Fixing permissions on /app/output..."
chmod 777 /app/output || true
chgrp 0 /app/output || true
chmod g+rwX /app/output || true

# Start your app
exec uvicorn main:app --host 0.0.0.0 --port 8000
