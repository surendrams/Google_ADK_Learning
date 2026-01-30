
#!/bin/bash
# scripts/01-setup-gcp.sh
# Step 1: GCP Project Setup
# Enables necessary APIs.

# Exit immediately if a command exits with a non-zero status.
set -e

# Check if PROJECT_ID is set
PROJECT_ID=${GOOGLE_CLOUD_PROJECT}

if [ -z "${PROJECT_ID}" ]; then
  echo "Error: GOOGLE_CLOUD_PROJECT environment variable is not set."
  echo "Please set it to your Google Cloud project ID."
  exit 1
fi

echo "🚀 Starting GCP Project Setup for ${PROJECT_ID}"

# --- API Enablement ---
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable \
    aiplatform.googleapis.com \
    texttospeech.googleapis.com \
    storage.googleapis.com \
    --project="${PROJECT_ID}"

echo "✅ APIs enabled."
