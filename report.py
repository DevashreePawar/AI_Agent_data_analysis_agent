# =============================================================
#  report.py — The Agent's "Voice"
# =============================================================
#
#  After the agent finishes its ReAct loop, it has collected
#  a log of every Thought, Action, and Observation.
#  This module takes that log and asks Llama-3.1-8B-Instruct
#  (via Groq) to write a clean, human-readable Markdown report
#  — just like a data analyst would write for a client.
#
#  KEY CONCEPT: Summarisation
#  Raw observations like "Mean: 24000.50" are not useful to
#  a business stakeholder. The LLM's job here is to interpret
#  the numbers and write meaningful insights in plain English.
# =============================================================

import os
from openai import OpenAI


# ── Model & API Config ─────────────────────────────────────────
MODEL_ID      = "llama-3.1-8b-instant"   # Groq's Llama-3.1-8B-Instruct
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def generate_report(history: list[dict], dataset_name: str) -> str:
    """
    Ask Llama-3.1-8B-Instruct (via Groq) to produce a structured
    Markdown analysis report.

    HOW IT WORKS:
    1.  We collect all the raw Thought/Action/Observation entries
        from the agent loop into a single text block.
    2.  We send that block to Llama via Groq with a prompt asking
        it to write a professional report.
    3.  We save the output to output/report.md and return the text.

    Args:
        history     : List of dicts from the ReAct loop, each with
                      keys 'thought', 'action', and 'observation'.
        dataset_name: Name of the CSV file (used in the report title).

    Returns:
        The full Markdown report as a string.
    """

    # ── Step 1: Flatten the agent history into readable text ──
    history_text = ""
    for i, entry in enumerate(history, 1):
        history_text += f"Step {i}:\n"
        history_text += f"  Thought    : {entry.get('thought', '')}\n"
        history_text += f"  Action     : {entry.get('action', '')}\n"
        history_text += f"  Observation: {entry.get('observation', '')}\n\n"

    # ── Step 2: Build the prompt ───────────────────────────────
    system_prompt = (
        "You are a professional data analyst. Your task is to read an analysis "
        "log and write a well-structured Markdown report based ONLY on the data "
        "in the log. Do not invent numbers or facts not present in the log."
    )

    user_prompt = f"""Below is a log of analysis steps performed on the dataset "{dataset_name}".
Each step shows what was analysed (Thought), what tool was run (Action), and what the tool returned (Observation).

=== ANALYSIS LOG ===
{history_text}
=== END LOG ===

Based on ONLY the information in the log above, write a professional Markdown report with the following sections:

# Data Analysis Report: {dataset_name}

## 1. Dataset Overview
Briefly describe the dataset: number of rows, columns, and data types found.

## 2. Key Statistics
Summarise the important numeric statistics found (mean, median, std, etc.).
Highlight anything noteworthy (high variance, skewed distributions, etc.).

## 3. Correlation Insights
Explain the strongest correlations found. What do they suggest?

## 4. Outliers & Anomalies
Describe any outliers detected and what they might mean.

## 5. Category Breakdown
Summarise any categorical column findings (e.g. top regions, products).

## 6. Key Takeaways & Recommendations
3–5 bullet points: the most important insights a business user should act on.

Write in clear, professional English. Be concise but specific. Use the actual numbers from the log."""

    # ── Step 3: Call Llama via Groq ────────────────────────────
    client = OpenAI(
        base_url=GROQ_BASE_URL,
        api_key=os.environ["GROQ_API_KEY"],
    )

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        max_tokens=2048,
        temperature=0.2,
    )
    report_text = response.choices[0].message.content.strip()

    # ── Step 4: Save to file ───────────────────────────────────
    os.makedirs("output", exist_ok=True)
    report_path = os.path.join("output", "report.md")
    with open(report_path, "w") as f:
        f.write(report_text)

    print(f"\n✅ Report saved → {report_path}")
    return report_text
