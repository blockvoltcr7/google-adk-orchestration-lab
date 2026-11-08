#!/usr/bin/env bash
set -e

SERVICE_NAME="${1:-lead-qualification-service}"
REGION="${2:-us-central1}"
PROJECT_ID="$(gcloud config get-value project)"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: No active GCP project configured in gcloud."
    exit 1
fi

echo "============================================================"
echo "Deploying to Google Cloud Run"
echo "Service: ${SERVICE_NAME}"
echo "Project: ${PROJECT_ID}"
echo "Region:  ${REGION}"
echo "============================================================"

gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --region "${REGION}" \
    --project "${PROJECT_ID}" \
    --allow-unauthenticated \
    --set-env-vars "ADK_MODEL=gemini-2.5-flash,GOOGLE_GENAI_USE_VERTEXAI=True" \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5

echo "============================================================"
echo "Deployment Complete!"
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --project "${PROJECT_ID}" --format="value(status.url)")
echo "Service URL: ${SERVICE_URL}"
echo "Health Check: curl -X GET ${SERVICE_URL}/health"
echo "============================================================"
