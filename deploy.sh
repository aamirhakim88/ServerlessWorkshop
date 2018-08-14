#!/bin/bash

# CONSTANTS
# ==========================================
# PROFILE="default"
STEP=""
VERSION_FOLDER=""
BUCKET_NAME="workshop-2018-deployment"
declare -a LAMBDA_FOLDER_ARRAY=("ChaosTraderGetStatus" "ChaosTraderMaster" "ChaosTraderWorker")
PROJECT_ROOT=$(pwd)
# ==========================================

while getopts p:s: option
do
  case "${option}" in
    # p) PROFILE=${OPTARG};;
    s) STEP=${OPTARG};;
  esac
done

# export AWS_PROFILE=${PROFILE}

set_version_folder()
{
  read -p "Enter Version Option [1 (Unoptimized) | 2 (Optimized)]: " version
  case ${version} in
    1)
      VERSION_FOLDER="before"
      break
      ;;
    2)
      VERSION_FOLDER="after"
      break
      ;;
  esac
  return 0
}

case ${STEP} in
  0)
    STEP_FOLDER="0-chaos-trader"
    break
    ;;
  1)
    STEP_FOLDER="1-instrument-app"
    set_version_folder
    STEP_FOLDER="${STEP_FOLDER}/${VERSION_FOLDER}"
    break
    ;;
  2)
    STEP_FOLDER="2-dependency-management"
    set_version_folder
    STEP_FOLDER="${STEP_FOLDER}/${VERSION_FOLDER}"
    break
    ;;
  3)
    STEP_FOLDER="3-connection-reuse"
    set_version_folder
    STEP_FOLDER="${STEP_FOLDER}/${VERSION_FOLDER}"
    break
    ;;
  4)
    STEP_FOLDER="4-synthetic"
    set_version_folder
    STEP_FOLDER="${STEP_FOLDER}/${VERSION_FOLDER}"
    break
    ;;
  5)
    STEP_FOLDER="5-parallel-processing"
    set_version_folder
    STEP_FOLDER="${STEP_FOLDER}/${VERSION_FOLDER}"
    break
    ;;
  6)
    STEP_FOLDER="6-right-sizing"
    set_version_folder
    STEP_FOLDER="${STEP_FOLDER}/${VERSION_FOLDER}"
    break
    ;;
  *)
    echo "Incorrect Input"
    exit 1
    ;;
esac

find . -type f -name "lambda.zip" -exec rm {} \;

for CURRENT_FOLDER in "${LAMBDA_FOLDER_ARRAY[@]}"
do
  echo "Compressing ${CURRENT_FOLDER} Lambda"
  cd ${STEP_FOLDER}/${CURRENT_FOLDER}
  zip -r -9 -y lambda.zip * > /dev/null
  cd ${PROJECT_ROOT}
done

if [ ${STEP} -eq 4 ];
then
  echo "Compressing Synthetic Lambda"
  CURRENT_FOLDER="Synthetic"
  cd ${STEP_FOLDER}/${CURRENT_FOLDER}
  zip -r -9 -y lambda.zip * > /dev/null
  cd ${PROJECT_ROOT}
fi

aws s3 mb \
  s3://${BUCKET_NAME}-$(aws sts get-caller-identity --output text --query 'Account') \
  --region ap-south-1 \

sam package \
  --region ap-south-1 \
  --template-file ${STEP_FOLDER}/template.yaml \
  --output-template-file ${STEP_FOLDER}/serverless-output.yaml \
  --s3-bucket ${BUCKET_NAME}-$(aws sts get-caller-identity --output text --query 'Account') \


sam deploy \
  --region ap-south-1 \
  --template-file ${STEP_FOLDER}/serverless-output.yaml \
  --stack-name workshop-2018-deployment-$(aws sts get-caller-identity --output text --query 'Account') \
  --capabilities CAPABILITY_IAM

if [ ${STEP} -eq 0 ];
then
  aws s3 cp \
    web \
    s3://chaostraderwebsitebucket$(aws sts get-caller-identity --output text --query 'Account') \
    --recursive \
    --acl public-read \
    > /dev/null

    python3 UIConfigCreator.py
fi

python3 apigwCORS.py

aws cloudformation describe-stacks \
  --region ap-south-1 \
  --stack-name workshop-2018-deployment-$(aws sts get-caller-identity --output text --query 'Account') \
  --query 'Stacks[].Outputs'
