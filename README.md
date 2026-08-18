# Building Agents Using the Amazon Bedrock API

This repository contains examples for building agents with the Amazon Bedrock API from Python.

## Prerequisites

- An AWS account with Amazon Bedrock enabled in the AWS Region you plan to use.
- Conda or Miniconda.
- AWS CLI v2.
- IAM permissions to list Bedrock foundation models and invoke the models you select. A least-privilege policy should be used for real workloads.

> **Security:** Never commit AWS access keys, secret keys, session tokens, or `.env` files to this repository. The commands below configure credentials in your local AWS profile. Use temporary credentials whenever possible and rotate them according to your organization's policy.

## 1. Create the Conda environment

From the repository root, create and activate a Conda environment named `aws_env`:

```bash
conda create --name aws_env python --yes
conda activate aws_env
```

Confirm that the environment is active and that Python is available:

```bash
conda env list
python --version
which python
```

Install the Python libraries required to integrate with Amazon Bedrock:

```bash
pip install -r requirements.txt
```

`boto3` is the AWS SDK for Python. `botocore` provides the underlying AWS request, credential, and region handling used by the SDK. For applications that load non-secret settings from a local `.env` file, you may also install `python-dotenv`:

```bash
python -m pip install python-dotenv
```

Do not put credentials in `.env`; use it only for values such as `AWS_REGION`.

## 2. Install and verify the AWS CLI

Install AWS CLI v2 using the [official AWS installation instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html), then verify it is available:

```bash
aws --version
```

The AWS CLI and `boto3` use the same standard AWS credential sources. Therefore, a valid AWS CLI profile can be used by Python without copying credentials into application code.

## 3. Configure AWS credentials on Linux

Run the interactive configuration command:

```bash
aws configure
```

Provide the requested values:

```text
AWS Access Key ID     : <access-key-id>
AWS Secret Access Key : <secret-access-key>
Default region name   : us-east-1
Default output format : json
```

`aws configure` stores the access key ID and secret access key in `~/.aws/credentials`, and the Region and output format in `~/.aws/config`. Do not paste real credentials into documentation, source code, or shell commands that may be saved in shell history.

### Add a temporary session token

`aws configure` does not prompt for a session token. If the credentials are temporary, add the token to the default profile with:

```bash
aws configure set aws_session_token '<session-token>'
```

Alternatively, keep the token only in the current shell session:

```bash
export AWS_ACCESS_KEY_ID='<access-key-id>'
export AWS_SECRET_ACCESS_KEY='<secret-access-key>'
export AWS_SESSION_TOKEN='<session-token>'
export AWS_REGION='us-east-1'
```

Do not use both profile credentials and environment credentials unintentionally. AWS SDKs typically give environment variables precedence over the shared profile.

For a named profile, use the profile consistently when configuring and testing:

```bash
aws configure --profile bedrock-dev
aws configure set aws_session_token '<session-token>' --profile bedrock-dev
export AWS_PROFILE=bedrock-dev
export AWS_REGION=us-east-1
```

### Verify the local AWS connection

First inspect which values the CLI is resolving. Secret values are masked:

```bash
aws configure list
```

Then verify that the active identity can authenticate with AWS:

```bash
aws sts get-caller-identity
```

The response should contain the AWS account ID, principal ID, and ARN. This is the first checkpoint in the setup pipeline. If it fails, resolve the credential, profile, Region, or network issue before testing Bedrock.

## 4. Verify Bedrock access from Python

Create a temporary file named `check_bedrock.py` with this read-only check:

```python
import os

import boto3


region = os.getenv("AWS_REGION", "us-east-1")
client = boto3.client("bedrock", region_name=region)

response = client.list_foundation_models()
models = response.get("modelSummaries", [])

print(f"Connected to Amazon Bedrock in {region}")
print(f"Found {len(models)} foundation models")
for model in models[:5]:
	print(f"- {model['modelId']}: {model['modelName']}")
```

Run it while `aws_env` is active and the AWS profile is selected:

```bash
python check_bedrock.py
```

This uses the Bedrock control-plane client and does not invoke a model. To invoke a model later, create a `bedrock-runtime` client and confirm that the target model is available in the selected Region and that the account has access to it.

## Common issues

- **`Unable to locate credentials`:** Confirm that `conda activate aws_env` was run and that `aws configure list` shows a configured credential source.
- **`AccessDeniedException`:** Ask an AWS administrator to grant the required Bedrock permissions and model access.
- **`ResourceNotFoundException`:** Check that the model ID and AWS Region are correct.
- **Model access unavailable:** Review model access or Marketplace requirements in the Amazon Bedrock console for the selected Region.
- **Unexpected profile or Region:** Run `aws configure list --profile "$AWS_PROFILE"` and inspect `AWS_PROFILE` and `AWS_REGION`.

Deactivate the Conda environment when finished:

```bash
conda deactivate
```
