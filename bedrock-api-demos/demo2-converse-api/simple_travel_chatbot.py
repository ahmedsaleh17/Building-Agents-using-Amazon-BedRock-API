import boto3 


# ---------------------------------------------------------------------------
# Bedrock client 
# ---------------------------------------------------------------------------
def bedrock_connection(region):
    """Create a Bedrock Runtime client for the requested AWS Region.

    Args:
        region: AWS Region where the model is available and enabled.

    Returns:
        A boto3 Bedrock Runtime client configured for ``region``.
    """
    return boto3.client("bedrock-runtime", region_name=region)


REGION = "us-east-1"

MODEL_ID = "amazon.nova-lite-v1:0"

SYSTEM_PROMPT = """\
You are a friendly travel assistant. Help users explore destinations, plan itineraries, \
and answer travel questions. Keep your answers concise and conversational."""


def run_chat():
    # messages to maintain conversation history 
    messages = []

    print("Travel Assistant: Hello! I can help you plan you next trip. Where are you thinking of going?\n")

    while True: 
        try: 
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt): 
            print("\nGood Bye :)")
            break

        if not user_input: 
            continue 

        messages.append({"role":"user", "content":[{"text": user_input}]})


        # invoke the bedrock model api using converse 
        bedrock = bedrock_connection(region= REGION)
        response = bedrock.converse(
            modelId=MODEL_ID, 
            system=[{"text": SYSTEM_PROMPT}],
            messages=messages
        )

        output_message = response["output"]["message"]
        messages.append(output_message)

        reply = output_message["content"][0]["text"]

        print(f"\nTravel Assistant: {reply}")



if __name__ == "__main__":
    run_chat()



"""
OutPut: 

Travel Assistant: Hello! I can help you plan you next trip. Where are you thinking of going?

You: i want to travel to germany, what do you recommend? 

Travel Assistant: Germany is a fantastic destination! Here’s a quick guide to get you started:

**Top Cities to Visit:**
1. **Berlin**: Explore historic sites like the Brandenburg Gate, visit museums like the Pergamon, and enjoy vibrant nightlife.
2. **Munich**: Discover the famous Marienplatz, take a day trip to Neuschwanstein Castle, and enjoy the beer gardens.
3. **Hamburg**: Stroll along the harbor, visit the Miniatur Wunderland, and explore the St. Michael's Church.

**Must-See Attractions:**
- **Black Forest (Schwarzwald)**: Scenic hiking trails and charming villages.
- **Rhine River**: Take a cruise and see the picturesque castles and vineyards.
- **The Bavarian Alps**: Perfect for hiking and skiing.

**Itinerary Ideas:**
- **7-Day Itinerary**: Berlin (2 days) → Munich (2 days) → Neuschwanstein Castle (1 day) → Hamburg (2 days)
- **10-Day Itinerary**: Berlin → Hamburg → Lübeck → Bremen → Cologne → Frankfurt → Heidelberg → Black Forest

**Travel Tips:**
- **Transportation**: The train system is efficient; consider a rail pass.
- **Language**: Basic German phrases can be helpful, but English is widely understood.
- **Currency**: The euro (€).

Enjoy your trip to Germany! 🌍🇩🇪
"""