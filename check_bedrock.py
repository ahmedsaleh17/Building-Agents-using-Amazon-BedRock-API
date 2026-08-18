import os 
import boto3 
from dotenv import load_dotenv

# Load key-value pairs from the .env file into the system environment
load_dotenv()

region = os.getenv("AWS_REGION")
# connect to amz Bedrock 
client = boto3.client("bedrock", region_name = region)



# check response 
response = client.list_foundation_models()

# get all foundation models summaries 
models = response.get("modelSummaries", [])

print(f"Connected to Amazon Bedrock in {region}")
print(f"Found {len(models)} Foundation models")


for model in models[:5]:
    print(f"- {model['modelId']} : {model["modelName"]}")



"""
OutPut: 
Connected to Amazon Bedrock in us-east-1
Found 122 Foundation models
- nvidia.nemotron-nano-12b-v2 : NVIDIA Nemotron Nano 12B v2 VL BF16
- qwen.qwen3-coder-next : Qwen3 Coder Next
- openai.gpt-5.6-terra : GPT-5.6 Terra
- anthropic.claude-sonnet-4-20250514-v1:0 : Claude Sonnet 4
- anthropic.claude-haiku-4-5-20251001-v1:0 : Claude Haiku 4.5


"""