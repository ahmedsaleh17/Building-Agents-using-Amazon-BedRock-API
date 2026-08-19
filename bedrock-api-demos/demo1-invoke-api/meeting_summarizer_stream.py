"""Summarize meeting notes with an Amazon Bedrock foundation model."""

import json

import boto3

# ---------------------------------------------------------------------------
# Sample meeting notes
# ---------------------------------------------------------------------------
MEETING_NOTES = """\
Meeting – Q3 Product Review
Date: Thursday afternoon
Attendees: Sarah (PM), Jake (Eng Lead), Priya (Design), Tom (QA)

Started about 10 minutes late. Sarah opened by saying the search feature is running
roughly two weeks behind schedule because the ranking algorithm keeps failing QA.
Tom confirmed three test cases are still red.

Jake said the core indexing work is done and the delay is entirely on ranking.
He proposed cutting the fuzzy-match feature from v1 and shipping exact-match only
to hit the release date. Sarah agreed; fuzzy-match moves to the backlog.

Priya raised a concern: the empty-state illustration hasn't been reviewed yet.
Sarah asked Priya to share it in Slack by Friday EOD for async feedback.

Budget question came up: Jake mentioned the new search infrastructure will add
roughly $2000/month to the AWS bill. Sarah said she'd confirm with Finance
whether that fits Q3 budget before the next sprint.

Wrap-up: next sync same time next week.
"""




# ---------------------------------------------------------------------------
# Bedrock client and streaming InvokeModel call
# ---------------------------------------------------------------------------
def bedrock_connection(region):
    """Create a Bedrock Runtime client for the requested AWS Region.

    Args:
        region: AWS Region where the model is available and enabled.

    Returns:
        A boto3 Bedrock Runtime client configured for ``region``.
    """
    return boto3.client("bedrock-runtime", region_name=region)



def summarize_notes_stream(notes):
    """Stream a meeting summary as Bedrock generates each text fragment.

    Args:
        notes: Raw meeting notes to send to the language model.

    Returns:
        None. Text fragments are written directly to standard output as they
        arrive, followed by a newline when the stream is complete.

    Raises:
        botocore.exceptions.ClientError: If AWS authentication, permissions,
            model access, or the Bedrock request fails.
        json.JSONDecodeError: If Bedrock returns a response that is not valid
            JSON.
        KeyError: If the model response does not contain the expected fields.
    """

    # The model ID and Region must refer to a model available in the
    # configured AWS account and Region.
    region = "us-east-1"
    model_id = "amazon.nova-pro-v1:0"
    bedrock = bedrock_connection(region)

    # Keep the requested output structure explicit so the model produces a
    # useful summary for downstream review.
    prompt = (
        "Summarize the following meeting notes into:\n"
        "1. Key decisions made\n"
        "2. Action items with owners\n\n"
        "Meeting notes:\n"
        "<notes>\n"
        f"{notes}\n"
        "/<notes>\n"
    )


    body = {
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"maxTokens": 512, "temperature": 0.0},
    }

    # The streaming API returns an event stream instead of one complete body.
    response = bedrock.invoke_model_with_response_stream(
        modelId=model_id, 
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )

    for event in response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if "contentBlockDelta" in chunk:
            text = chunk["contentBlockDelta"]["delta"].get("text", "")
            # Flush each fragment so the user sees the summary immediately.
            print(text, end="", flush=True)

    print()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    print("=== StreamInvokeModel ===\n")
    summarize_notes_stream(MEETING_NOTES)