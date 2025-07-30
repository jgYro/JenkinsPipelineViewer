#!/bin/bash

USER="Yro"
TOKEN="9106c1c8ffb9ca0ca3c5ee102791df0d"
BASE_URL="http://localhost:8080"
PIPELINE="CC3"
BRANCH="master"

# Get latest run ID
RUN_ID=$(curl -s -u "$USER:$TOKEN" \
  "$BASE_URL/blue/rest/organizations/jenkins/pipelines/$PIPELINE/branches/$BRANCH/runs/?limit=1" \
  | jq -r '.[0].id')

# Get all stages (nodes)
STAGE_IDS=$(curl -s -u "$USER:$TOKEN" \
  "$BASE_URL/blue/rest/organizations/jenkins/pipelines/$PIPELINE/branches/$BRANCH/runs/$RUN_ID/nodes/" \
  | jq -r '.[].id')

# Get all steps per stage
for STAGE_ID in $STAGE_IDS; do
  echo "== Stage ID: $STAGE_ID =="
  curl -s -u "$USER:$TOKEN" \
    "$BASE_URL/blue/rest/organizations/jenkins/pipelines/$PIPELINE/branches/$BRANCH/runs/$RUN_ID/nodes/$STAGE_ID/steps/" \
    | jq '.'
done
