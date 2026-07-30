"""Amazon Bedrock AI service integration using Converse API for Amazon Nova."""
import json
import boto3
from backend.config import AWS_REGION, BEDROCK_MODEL_ID
from backend.prompts.analyze_change import build_analyze_prompt
from backend.prompts.missing_info import build_missing_info_prompt
from backend.prompts.hitl_chat import build_hitl_system_prompt, build_hitl_user_message
from backend.prompts.guardrail_check import build_guardrail_prompt
from backend.prompts.query_memory import build_query_prompt


def get_bedrock_client():
    """Create a Bedrock runtime client."""
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


def invoke_bedrock(prompt: str, system_prompt: str = None, max_tokens: int = 4096) -> str:
    """Invoke Amazon Bedrock using the Converse API (works with Amazon Nova models).

    Args:
        prompt: The user message content
        system_prompt: Optional system-level instruction
        max_tokens: Maximum tokens in response

    Returns:
        The response text from the model
    """
    client = get_bedrock_client()

    # Build messages
    messages = [
        {
            "role": "user",
            "content": [{"text": prompt}]
        }
    ]

    # Build kwargs for converse
    kwargs = {
        "modelId": BEDROCK_MODEL_ID,
        "messages": messages,
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": 0.1,
        },
    }

    # Add system prompt if provided
    if system_prompt:
        kwargs["system"] = [{"text": system_prompt}]

    response = client.converse(**kwargs)

    # Extract response text
    output = response.get("output", {})
    message = output.get("message", {})
    content = message.get("content", [])

    if content:
        return content[0].get("text", "")

    return ""


def parse_json_response(text: str) -> dict:
    """Extract JSON from AI response, handling markdown code blocks."""
    text = text.strip()

    # Remove markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    # Find JSON object in text
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    return {"error": "Failed to parse AI response", "raw": text}


def analyze_documents(documents_text: str) -> dict:
    """Analyze documents to detect change type and generate reasoning."""
    prompt = build_analyze_prompt(documents_text)
    response = invoke_bedrock(prompt)
    return parse_json_response(response)


def detect_missing_info(reasoning: dict, change_type: str) -> dict:
    """Detect missing information in reasoning record."""
    prompt = build_missing_info_prompt(
        reasoning=json.dumps(reasoning, indent=2),
        change_type=change_type
    )
    response = invoke_bedrock(prompt)
    return parse_json_response(response)


def run_guardrail_check(reasoning: dict, documents_text: str) -> dict:
    """Run guardrail checks on AI output."""
    prompt = build_guardrail_prompt(
        reasoning=json.dumps(reasoning, indent=2),
        documents=documents_text[:5000]
    )
    response = invoke_bedrock(prompt)
    return parse_json_response(response)


def hitl_chat(question: str, change_type: str, reasoning: dict, documents_text: str) -> dict:
    """Handle HITL chat interaction with system context."""
    system = build_hitl_system_prompt(
        change_type=change_type,
        reasoning=json.dumps(reasoning, indent=2),
        documents=documents_text[:5000]
    )
    user_msg = build_hitl_user_message(question)

    response = invoke_bedrock(user_msg, system_prompt=system, max_tokens=2048)
    return parse_json_response(response)


def query_verified_memory(question: str, memories_text: str) -> dict:
    """Query verified organizational memory."""
    prompt = build_query_prompt(
        memories=memories_text,
        question=question
    )
    response = invoke_bedrock(prompt)
    return parse_json_response(response)
