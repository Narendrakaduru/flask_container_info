#!/bin/bash

# Set these variables
ARGOCD_SERVER="192.168.1.240:8443"
ARGOCD_USERNAME="admin"
ARGOCD_PASSWORD="T0R8e9O@&GxB2V"
ARGOCD_APP="flask-container-info"

# Log in to Argo CD
argocd login $ARGOCD_SERVER \
  --username "$ARGOCD_USERNAME" \
  --password "$ARGOCD_PASSWORD" \
  --insecure \
  --grpc-web

# Trigger sync
argocd app sync $ARGOCD_APP

# Wait for sync and healthy status
argocd app wait $ARGOCD_APP --health --operation