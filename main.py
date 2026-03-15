# =============================================================
#  main.py — The Entry Point
# =============================================================
#
#  This is the only file you need to run. It:
#  1. Reads the HuggingFace API token from your .env file
#  2. Accepts a CSV filepath from the command line
#  3. Kicks off the agent loop (Llama-3.1-8B-Instruct via HF)
#  4. Triggers report generation
#  5. Prints the report to the console
#
#  HOW TO RUN:
#    python3 main.py data/sample_sales.csv
#
#  HOW ENVIRONMENT VARIABLES WORK:
#  We never hardcode API keys in source code (security risk!).
#  Instead we store them in a .env file and use python-dotenv
#  to load them into os.environ at runtime.
#
#  GETTING YOUR GROQ_API_KEY (free, no credit card):
#  1. Go to https://console.groq.com
#  2. Sign up / log in → API Keys → Create API Key
#  3. Paste the key into your .env file as GROQ_API_KEY=gsk_xxx
# =============================================================

import os
import sys
from dotenv import load_dotenv

from agent import run_agent, MODEL_ID
from report import generate_report


def main():
    # ── Step 1: Load environment variables from .env ──────────
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key or api_key == "gsk_your_key_here":
        print("❌  ERROR: GROQ_API_KEY not set!")
        print()
        print("  To fix this:")
        print("  1. Go to https://console.groq.com")
        print("  2. Sign up / Log in → API Keys → Create API Key")
        print("  3. Open .env and set:  GROQ_API_KEY=gsk_your_key_here")
        sys.exit(1)

    # ── Step 2: Determine the dataset to analyse ──────────────
    if len(sys.argv) < 2:
        # Default to the sample dataset if no argument given
        filepath = "data/sample_sales.csv"
        print(f"ℹ️  No file specified. Using default: {filepath}")
    else:
        filepath = sys.argv[1]

    if not os.path.exists(filepath):
        print(f"❌  File not found: {filepath}")
        sys.exit(1)

    dataset_name = os.path.basename(filepath)
    print(f"\n📂  Dataset  : {filepath}")
    print(f"🦙  Model    : Llama-3.1-8B-Instruct")
    print(f"⚡  Provider : Groq (free tier)")
    print(f"📁  Output   : ./output/")

    # ── Step 4: Run the ReAct Agent Loop ──────────────────────
    #
    #  This is where the magic happens. The agent will:
    #  - Load the data
    #  - Explore it step by step (Thought → Action → Observation)
    #  - Stop when it decides it has enough information
    #
    history = run_agent(filepath, max_steps=15)

    # ── Step 5: Generate the Final Report ─────────────────────
    #
    #  The agent's raw observations are passed to the report
    #  generator which asks Llama to turn them into a
    #  professional, readable markdown report.
    #
    print("\n📝  Generating final report...")
    report_text = generate_report(history, dataset_name)

    # ── Step 6: Display the Report ────────────────────────────
    print("\n" + "=" * 60)
    print("  📄  FINAL REPORT")
    print("=" * 60)
    print(report_text)
    print("=" * 60)
    print(f"\n📁  Saved: output/report.md")
    if os.path.exists("output"):
        charts = [f for f in os.listdir("output") if f.endswith(".png")]
        if charts:
            print(f"📊  Charts: {', '.join(charts)}")
    print("\n✅  Done! Your analysis is complete.\n")


if __name__ == "__main__":
    main()
