#!/bin/bash

# Fast deployment script for Google Cloud Run
# Uses Cloud Build for parallel builds and caching

set -e  # Exit on error

# Configuration
PROJECT_ID="gen-lang-client-0634737684"
SERVICE_NAME="commerce-backend"
REGION="us-central1"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting deployment to Cloud Run...${NC}"

# Check if we should use Cloud Build (faster) or local build
if command -v gcloud &> /dev/null; then
    echo -e "${GREEN}Using Cloud Build for faster deployment...${NC}"

    # Submit to Cloud Build (builds in parallel on Google's infrastructure)
    gcloud builds submit --config cloudbuild.yaml --project $PROJECT_ID

    echo -e "${GREEN}✅ Deployment complete!${NC}"
    echo -e "${BLUE}Service URL:${NC}"
    gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
else
    echo -e "${RED}gcloud CLI not found. Please install Google Cloud SDK.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Tip: Use 'gcloud run services logs read $SERVICE_NAME --region $REGION' to view logs${NC}"
