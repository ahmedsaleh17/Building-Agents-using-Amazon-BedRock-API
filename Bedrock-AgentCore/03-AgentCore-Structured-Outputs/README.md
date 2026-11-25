# Structured Outputs and Pydantic Validation

This example builds WanderBot with Strands, Amazon Bedrock, and the Bedrock
AgentCore Runtime. The Pydantic models in `demo.py` define the expected shapes
of flight-search data. The search tool validates its inputs and data, then
serializes valid results as JSON.

## What happens in `demo.py`

1. AgentCore receives a request with a `message`.
2. The Strands agent receives the message and can call `search_flights`.
3. `FlightSearchInput` validates the tool arguments before the tool searches
   `datasets/flights_broken.json`.
4. Each matching record is checked against `FlightOption`. Invalid records are
   logged and skipped.
5. The remaining records and their count are put into a `FlightSearchResult`.
   `model_dump_json()` serializes this Pydantic model as JSON for the agent.

| Model | Purpose |
| --- | --- |
| `FlightSearchInput` | Checks the types of `origin`, `destination`, and `date`. |
| `FlightOption` | Defines a flight record; `available_seats` must be non-negative. |
| `FlightSearchResult` | Defines the result object with `flights` and `total`. |

The `date` field is a string in this example; Pydantic does not check that it
matches a real calendar date or the `YYYY-MM-DD` format. Add a date type or
validator if that stronger check is required.

When input validation fails, the tool returns a JSON error. If the dataset
cannot be read or parsed, it returns an availability error. When a flight
record fails validation, the tool logs a warning and omits that record.

## Tool JSON is not the final agent response

The tool returns JSON, but that does not make the agent's final response JSON.
As currently written, `invoke()` calls `agent(user_message)` and returns the
regular Strands result. The model may respond in natural language. A system
prompt asking for JSON is guidance, not enforcement.

To request the final response in the `FlightSearchResult` shape, replace the
regular invocation in `invoke()` with Strands structured output:

```python
response = agent.structured_output(
    output_model=FlightSearchResult,
    prompt=user_message,
)
return response.model_dump()
```

This asks the model for the declared output schema and returns a
JSON-serializable Python dictionary. Use `response.model_dump_json()` if the
caller specifically needs a JSON string. Structured output and Pydantic
validation provide a schema-checked response instead of relying on prompt
instructions alone. Handle model or validation errors explicitly in production.

`FlightSearchResult` contains only `flights` and `total`, so the final response
will follow that shape rather than include extra prose. Confirm that the
installed Strands version and selected Bedrock model support structured output;
see the [Strands structured-output guide](https://strandsagents.com/docs/user-guide/sdk/agents/structured-output/)
for details.

## Run locally

From this directory, install the packages:

```bash
pip install -r requirements.txt
```

Configure AWS credentials and ensure the selected region/account can invoke
`us.amazon.nova-2-lite-v1:0`. Install and verify the AgentCore CLI if needed:

```bash
pip install uv
uv pip install bedrock-agentcore-starter-toolkit
agentcore --help
```

Start the local runtime:

```bash
agentcore configure
agentcore dev
```

In another terminal, invoke it:

```bash
agentcore invoke --dev '{"message": "Find flights from LHR to CDG on 2026-03-15"}'
```

## Deploy

After local testing, deploy and invoke the app:

```bash
agentcore deploy --auto-update-on-conflict
agentcore invoke '{"message": "Find flights from LHR to CDG on 2026-03-15"}'
```
