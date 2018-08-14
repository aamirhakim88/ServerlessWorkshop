#!/bin/bash

# ==========================================
PROFILE=default
while getopts p: option
do
  case "${option}" in
    p) PROFILE=${OPTARG};;
  esac
done
# ==========================================

export AWS_PROFILE=${PROFILE}

command -v npm >/dev/null 2>&1 || { echo >&2 "NPM Missing."; exit 1; }

# npm install serverless -g
serverless config credentials --profile ${PROFILE} --provider aws

# serverless install -u https://github.com/alexcasalboni/aws-lambda-power-tuning

cd aws-lambda-power-tuning
npm install

npm run generate \
  -- \
  -A $(aws sts get-caller-identity --output text --query 'Account') \
  -R ap-south-1 \
  -P 512,1024,1536,2048,2560,3008

serverless deploy
