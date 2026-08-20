# The `invoke_model` API

`invoke_model` is the low-level Bedrock primitive for calling a foundation model. It is intentionally minimal: the caller supplies a model ID, a model-specific request body, and a content type, and receives a single response back. It does not manage conversation state, normalize request/response formats across models, or route tool calls for you.

The walkthrough builds a meeting summarizer that takes raw notes and returns a structured summary with key decisions and action items. The same script is then converted to use the streaming variant — `invoke_model_with_response_stream` — to display tokens as they are generated.

**Boto3** is the official Amazon Web Services (AWS) Software Development Kit (SDK) for Python. It allows developers to write Python scripts to create, manage, and automate AWS resources like S3 buckets, EC2 instances, and DynamoDB tables directly from code.

## The four moving parts of an `invoke_model` call

| **Component**              |  **Purpose**             |
|----------------------------|--------------------------|
| **Bedrock Runtime client** | A `boto3` client created with `boto3.client("bedrock-runtime", region_name=...)`. The Bedrock Runtime service is the one that actually invokes models; the broader Bedrock service handles non-runtime concerns (prompt management, evaluations, etc.). |
| **Model ID**               | The full identifier the service uses to route the request to the right model (for example, `amazon.nova-pro-v1:0`).                                                                                                                                     |
| **Request body**           | A JSON payload whose shape depends on the model provider. The walkthrough uses Bedrock's converse-format messages list with a role-and-content structure plus an inference config block (max tokens, temperature).                                      |
| **Response parsing**       | A nested structure: `output.message.content[0].text` is the path to the generated text in the converse format. The application code is responsible for extracting it.                                                                                   |

The body format is the largest source of friction with `invoke_model`: each model provider expects its own shape, and the Amazon Bedrock user guide is the authoritative reference for which shape to use with which model.

## Synchronous vs. streaming invocation

The core difference is how data is delivered: **synchronous invocation** waits for the entire response to process before sending it all at once, whereas **streaming invocation** sends back data in small, continuous pieces (chunks) as it is being generated.

`invoke_model` waits for the full response before returning. For short outputs, this is fine. For longer generations or interactive applications, the request can pause for several seconds with no visible progress, which feels broken to a user.

`invoke_model_with_response_stream` returns response chunks as they are produced. The caller iterates over an event stream, extracts the text fragment from each event, and displays it as it arrives. The total wall-clock time is similar, but the perceived latency is much lower because output starts appearing within the first second.

Both methods take the same model ID, body, and content type. The only difference is which method is called and how the response is consumed.
