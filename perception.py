# ✅ Must come BEFORE any Google imports
import os

# Suppress gRPC / absl / TensorFlow logs globally
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GRPC_CPP_VERBOSITY"] = "NONE"
os.environ["GRPC_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# ────────────────────────────────────────────────
# Now safe to import Google SDKs and others
# ────────────────────────────────────────────────
import google.generativeai as genai
from dotenv import load_dotenv
import re

# ✅ Load .env file
load_dotenv()

# Configure Gemini with API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def perceive() -> str:
    """
    Generates factual insights from a predefined query using Google Gemini.
    Cleans and normalizes Gemini's response into simple, readable bullet points.
    """
    query = "Find ASCII values of characters in AMERICA, calculate sum of exponentials, and add result to input.pptx"

    prompt = f"""
    Extract the key facts from the given user query below.
    - Avoid introductions like "Sure" or "Here's what I found".
    
    Query: "{query}"
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    if not response.text:
        return "No facts generated."

    # 🧹 Step 1: Basic clean-up
    facts_raw = response.text.strip()

    # 🧹 Step 2: Remove any preamble before the first dash
    facts_clean = re.sub(r"(?i)^.*?(?=- )", "", facts_raw, flags=re.S)

    # 🧹 Step 3: Normalize bullet styles
    facts_clean = re.sub(r"^[\*\-\•\d\.\s]+", "- ", facts_clean, flags=re.M)

    # 🧹 Step 4: Strip blank lines
    lines = [line.strip() for line in facts_clean.splitlines() if line.strip()]
    cleaned_text = "\n".join(lines)

    return cleaned_text



