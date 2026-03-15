#!/usr/bin/env python3
# =============================================================
#  test_llama_connection.py — Quick connectivity test
# =============================================================
#  Verifies your GROQ_API_KEY works and the Llama model responds.
#
#  Usage:
#    python3 test_llama_connection.py
#
#  Expected output:
#    ✅  Connected! Llama says: "Paris" (or similar)
# =============================================================

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

token = os.getenv("GROQ_API_KEY")
if not token or token == "gsk_your_key_here":
    print("❌  GROQ_API_KEY not set in .env — please add your key first.")
    print()
    print("  1. Go to https://console.groq.com")
    print("  2. Sign up / Log in → API Keys → Create API Key")
    print("  3. Open .env and add:  GROQ_API_KEY=gsk_your_key_here")
    sys.exit(1)

MODEL_ID = "llama-3.1-8b-instant"
print(f"🔗  Connecting to Groq API  (model: {MODEL_ID})...")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=token,
)

try:
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "system", "content": "You are a concise assistant. Reply in one word only."},
            {"role": "user",   "content": "What is the capital of France?"},
        ],
        max_tokens=10,
        temperature=0.1,
    )
    answer = response.choices[0].message.content.strip()
    print(f"✅  Connected! Llama says: \"{answer}\"")
    print("\n🚀  Your setup is ready. Run the agent with:")
    print(f"    python3 main.py data/sample_sales.csv")
    sys.exit(0)

except Exception as e:
    print(f"❌  Connection failed: {e}")
    print("\nTroubleshooting tips:")
    print("  1. Make sure GROQ_API_KEY is set correctly in .env")
    print("  2. Verify the key at https://console.groq.com")
    print("  3. Check your internet connection")
    sys.exit(1)
