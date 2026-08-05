"""Amazon Bedrock AI service integration using Converse API for Amazon Nova."""
import json
import boto3
from backend.config import AWS_REGION, BEDROCK_MODEL_ID, BEDROCK_GUARDRAIL_ID, BEDROCK_GUARDRAIL_VERSION
from backend.prompts.analyze_change import build_analyze_prompt
from backend.prompts.missing_info import build_missing_info_prompt
from backend.prompts.hitl_chat import build_hitl_system_prompt, build_hitl_user_message
from backend.prompts.guardrail_check import build_guardrail_prompt
from backend.prompts.query_memory import build_query_prompt
from backend.prompts.groundedness_check import build_groundedness_prompt


def get_bedrock_client():
    """Create a Bedrock runtime client."""
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


def invoke_bedrock(prompt: str, system_prompt: str = None, max_tokens: int = 4096) -> str:
    """Invoke Amazon Bedrock using the Converse API with AWS Guardrails attached.

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
        # Attach AWS Bedrock Guardrail
        "guardrailConfig": {
            "guardrailIdentifier": BEDROCK_GUARDRAIL_ID,
            "guardrailVersion": BEDROCK_GUARDRAIL_VERSION,
            "trace": "enabled",
        },
    }

    # Add system prompt if provided
    if system_prompt:
        kwargs["system"] = [{"text": system_prompt}]

    response = client.converse(**kwargs)

    # Check if guardrail intervened
    stop_reason = response.get("stopReason", "")
    if stop_reason == "guardrail_intervened":
        # Get the guardrail trace for logging
        trace = response.get("trace", {}).get("guardrail", {})
        blocked_msg = "Content blocked by AWS Bedrock Guardrail."

        # Get output if any
        output = response.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])
        if content:
            blocked_msg = content[0].get("text", blocked_msg)

        raise GuardrailBlockedException(blocked_msg, trace)

    # Extract response text
    output = response.get("output", {})
    message = output.get("message", {})
    content = message.get("content", [])

    if content:
        text = content[0].get("text", "")
        # Replace AWS Bedrock anonymization placeholders with masked format
        text = replace_pii_placeholders(text)
        return text

    return ""


def replace_pii_placeholders(text: str) -> str:
    """Replace AWS Bedrock Guardrail PII placeholders with masked display format.

    Bedrock ANONYMIZE replaces PII with {TYPE} placeholders like:
    {US_SOCIAL_SECURITY_NUMBER}, {CREDIT_DEBIT_CARD_NUMBER}, {IP_ADDRESS}, etc.
    We convert these to a user-friendly masked format.
    """
    import re

    placeholder_map = {
        "US_SOCIAL_SECURITY_NUMBER": "###-##-####",
        "CREDIT_DEBIT_CARD_NUMBER": "####-####-####-####",
        "EMAIL": "######@######",
        "PHONE": "(###) ###-####",
        "US_BANK_ACCOUNT_NUMBER": "########",
        "US_PASSPORT_NUMBER": "#########",
        "US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER": "###-##-####",
        "DRIVER_ID": "DL#######",
        "IP_ADDRESS": "#.#.#.#",
        "URL": "https://######",
        "USERNAME": "######",
        "NAME": "######",
        "ADDRESS": "######",
        "AGE": "##",
        "DATE_TIME": "##/##/####",
        "AWS_ACCESS_KEY": "[AWS KEY REDACTED]",
        "AWS_SECRET_KEY": "[AWS SECRET REDACTED]",
        "PASSWORD": "[PASSWORD REDACTED]",
    }

    # Match {PLACEHOLDER_TYPE} patterns from Bedrock
    for pii_type, mask in placeholder_map.items():
        text = text.replace(f"{{{pii_type}}}", mask)

    # Catch any remaining {SOMETHING} guardrail placeholders
    text = re.sub(r'\{[A-Z_]+\}', '######', text)

    return text


class GuardrailBlockedException(Exception):
    """Raised when AWS Bedrock Guardrail blocks content."""
    def __init__(self, message: str, trace: dict = None):
        super().__init__(message)
        self.trace = trace or {}


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


def verify_groundedness(reasoning: dict, documents_text: str) -> dict:
    """Verify that AI reasoning is grounded in source documents with citations.

    This is an independent verification step — it checks whether each claim
    in the reasoning record can be traced back to a specific passage in the
    source documents.

    Args:
        reasoning: The AI-generated reasoning dict
        documents_text: The combined source document text

    Returns:
        dict with claims verification, groundedness score, and critical gaps
    """
    prompt = build_groundedness_prompt(
        reasoning=json.dumps(reasoning, indent=2),
        documents=documents_text[:8000]  # More context for better verification
    )
    response = invoke_bedrock(prompt)
    result = parse_json_response(response)

    # Ensure the result has expected structure
    if "claims" not in result:
        result = {
            "claims": [],
            "groundedness_score": {
                "supported": 0,
                "partially_supported": 0,
                "unsupported": 0,
                "total": 0,
                "percentage": 0,
            },
            "summary": "Groundedness verification could not be completed.",
            "critical_gaps": [],
        }

    # Recalculate score from claims to ensure consistency
    if result.get("claims"):
        claims = result["claims"]
        supported = sum(1 for c in claims if c.get("status") == "SUPPORTED")
        partial = sum(1 for c in claims if c.get("status") == "PARTIALLY_SUPPORTED")
        unsupported = sum(1 for c in claims if c.get("status") == "UNSUPPORTED")
        total = len(claims)
        # Percentage: fully supported = 100%, partially = 50% credit
        percentage = round(((supported + partial * 0.5) / total) * 100) if total > 0 else 0

        result["groundedness_score"] = {
            "supported": supported,
            "partially_supported": partial,
            "unsupported": unsupported,
            "total": total,
            "percentage": percentage,
        }

    return result
