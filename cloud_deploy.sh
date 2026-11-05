#!/usr/bin/env bash
# =============================================================================
# CAMPUSINTEL CLOUD RAG - CLOUD DEPLOYMENT SCRIPT
# Automated Deployment to AWS App Runner / AWS ECS Fargate
# =============================================================================

set -e

echo "=========================================================="
echo "DEPLOYING CAMPUSINTEL CLOUD RAG TO AWS CLOUD"
echo "=========================================================="

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "[!] AWS CLI is required for automated cloud deployment."
    echo "    Install via: https://aws.amazon.com/cli/"
    exit 1
fi

AWS_REGION=${AWS_REGION:-"us-east-1"}
APP_NAME="campusintel-cloud-rag"
ECR_REPO_NAME="campusintel-repo"

echo "[1/4] Authenticating Docker with Amazon ECR in ${AWS_REGION}..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

echo "[2/4] Ensuring ECR Repository exists..."
aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} --region ${AWS_REGION} || \
aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${AWS_REGION}

echo "[3/4] Building and Tagging Docker Container Image..."
docker build -t ${APP_NAME}:latest .
docker tag ${APP_NAME}:latest ${ECR_URI}/${ECR_REPO_NAME}:latest

echo "[4/4] Pushing Container Image to Amazon ECR..."
docker push ${ECR_URI}/${ECR_REPO_NAME}:latest

echo "=========================================================="
echo "[SUCCESS] Container successfully deployed to Amazon ECR!"
echo "Image URI: ${ECR_URI}/${ECR_REPO_NAME}:latest"
echo "You can now link this image to AWS App Runner or AWS ECS Fargate."
echo "=========================================================="
