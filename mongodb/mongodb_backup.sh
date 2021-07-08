#!/usr/bin/env bash

echo "Dumping MongoDB"
mongodump

echo "copying MongoDB dump to gcloud"
gsutil cp /dump/admin/system.version.bson gs://cp-uob/mongodb_backups
gsutil cp /dump/admin/system.version.metadata.json gs://cp-uob/mongodb_backups
