#!/bin/bash

echo "Waiting..."
sleep 5
alembic upgrade head
echo "FINISH UPGRADE.."
gunicorn app:app --bind=0.0.0.0:5000
