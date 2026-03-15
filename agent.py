# =============================================================
#  agent.py — The Agent's "Brain"
# =============================================================
#
#  This is the HEART of the project. It implements the
#  ReAct (Reasoning + Acting) loop — the most fundamental
#  pattern in agentic AI.
#
#  ┌─────────────────────────────────────────────────────┐
#  │                  ReAct Loop                         │
#  │                                                     │
#  │  ┌─────────┐    ┌────────┐    ┌──────────────────┐  │
#  │  │  THINK  │───▶│  ACT   │───▶│    OBSERVE       │  │
#  │  │ (LLM)   │    │(Python)│    │ (tool result)    │  │
#  │  └─────────┘    └────────┘    └──────────────────┘  │
#  │       ▲                               │             │
#  │       └───────────────────────────────┘             │
#  │                  (repeat)                           │
#  └─────────────────────────────────────────────────────┘
#
#  HOW IT WORKS (plain English):
#  1. We tell the LLM: "Here is a dataset. Here are your tools.
#     Analyse it step by step."
#  2. The LLM responds with a Thought (what to do next) and
#     an Action (which tool to call and with what arguments).
#  3. We parse the LLM's text, find the Action, and actually
#     run the corresponding Python function.
#  4. We feed the result (Observation) back to the LLM.
#  5. Repeat until the LLM says "FINISH".
#
#  KEY AGENTIC CONCEPTS DEMONSTRATED HERE:
#  - ReAct loop           : Think → Act → Observe → Repeat
#  - Tool use             : LLM selects and calls Python functions
#  - Autonomous planning  : LLM decides what to analyse next
#  - Memory via context   : Full history is re-sent each iteration
#  - Termination          : Agent decides when it's done
#
#  MODEL: Meta Llama-3.1-8B-Instruct served by Groq (free tier)
#  WHY GROQ: Fastest free inference for Llama models, no special
#            permissions required — just a simple API key.
# =============================================================

import os
import re
from openai import OpenAI
import tools as tool_module
from tools import TOOLS, TOOL_DESCRIPTIONS


# ── Model & API Config ─────────────────────────────────────────
MODEL_ID    = "llama-3.1-8b-instant"   # Groq model name for Llama-3.1-8B
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# ── System Prompt ─────────────────────────────────────────────
#
#  The system prompt is the instruction manual we give the LLM.
#  It defines the agent's persona, the output format it must
#  follow, and the rules it must obey.
#
#  WHY FORMAT MATTERS:
#  The LLM outputs plain text. To extract the Thought and Action
#  we need the output to follow a predictable structure.
#  We enforce this with explicit instructions.
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an expert data analyst AI agent. Your goal is to autonomously
explore a dataset and uncover meaningful insights.

You have access to the following tools:
{tool_descriptions}

You MUST respond in EXACTLY this format every turn:
Thought: <your reasoning about what to do next>
Action: <tool_name>(<arguments>)

Rules:
- Always call load_data first.
- After loading, call describe_data to understand the structure.
- Then systematically explore: stats, correlations, outliers, value counts.
- Plot histograms for the most important numeric columns.
- When you have gathered sufficient insights (at least 6–8 steps), write:
    Thought: I have gathered enough insights to write a comprehensive report.
    Action: FINISH
- Do NOT repeat the same Action twice.
- Arguments to tools are plain strings or nothing: compute_stats(revenue)
""".strip()


def _build_messages(filepath: str, conversation: list[str]) -> list[dict]:
    """
    Assemble the chat messages list to send to Llama via Groq API.

    We use the OpenAI chat format with a 'system' role for instructions
    and 'user' turns for the conversation history.

    WHY THIS FORMAT:
    Llama-3.1-8B-Instruct is trained with chat templates. Providing a
    proper system prompt plus alternating messages gives significantly
    better structured outputs than a single concatenated text block.
    """
    system_content = SYSTEM_PROMPT.format(tool_descriptions=TOOL_DESCRIPTIONS)

    messages = [{"role": "system", "content": system_content}]

    if not conversation:
        # First turn — bootstrap with the task
        messages.append({
            "role": "user",
            "content": (
                f"Begin analysing this dataset: {filepath}\n\n"
                "Respond with your first Thought and Action."
            )
        })
    else:
        # Pack the full conversation into a single user message so the
        # model sees everything that has happened and what to do next.
        history_block = "\n\n".join(conversation)
        messages.append({
            "role": "user",
            "content": (
                f"Dataset: {filepath}\n\n"
                f"Previous steps:\n{history_block}\n\n"
                "Continue the analysis. Respond with your next Thought and Action."
            )
        })

    return messages


def _parse_action(text: str):
    """
    Extract the tool name and argument from the LLM's action line.

    The LLM outputs lines like:
        Action: compute_stats(revenue)
        Action: value_counts(region)
        Action: FINISH

    We use regex to pull out the function name and its argument.

    Args:
        text: The full LLM response string.

    Returns:
        Tuple (tool_name: str, argument: str | None)
        Returns ("FINISH", None) if the agent is done.
        Returns (None, None) if parsing fails.
    """
    # Match "Action: tool_name(optional_arg)"
    match = re.search(r"Action:\s*(\w+)\(([^)]*)\)", text)
    if match:
        tool_name = match.group(1).strip()
        argument = match.group(2).strip().strip('"').strip("'")
        return tool_name, argument if argument else None

    # Match "Action: FINISH" (no parentheses)
    finish_match = re.search(r"Action:\s*(FINISH)", text, re.IGNORECASE)
    if finish_match:
        return "FINISH", None

    return None, None


def _parse_thought(text: str) -> str:
    """
    Extract the Thought text from the LLM response.

    Args:
        text: Full LLM response string.

    Returns:
        The Thought content as a string.
    """
    match = re.search(r"Thought:\s*(.+?)(?:\nAction:|$)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def run_agent(filepath: str, max_steps: int = 15) -> list[dict]:
    """
    Execute the ReAct agent loop on a given CSV file.

    This is the main function. It runs until:
    a) The LLM outputs "FINISH", or
    b) max_steps is reached (safety limit to control API costs).

    Args:
        filepath  : Path to the CSV dataset.
        max_steps : Maximum number of Thought→Action→Observe cycles.

    Returns:
        A list of history dicts, each containing:
            { 'thought': str, 'action': str, 'observation': str }
        This history is later used by report.py to generate the report.
    """

    print("\n" + "=" * 60)
    print("  🤖  AI DATA ANALYSIS AGENT  —  Starting ReAct Loop")
    print(f"  🦙  Model : Llama-3.1-8B-Instruct")
    print(f"  ⚡  via   : Groq (free tier)")
    print("=" * 60)

    # Tracks the entire conversation so the LLM always
    # has full context of what has been done so far.
    conversation: list[str] = []

    # Stores the structured Thought/Action/Observation history
    # for the report generator.
    history: list[dict] = []

    # Track actions already taken — avoid repeating them
    seen_actions: set[str] = set()

    # ── Create Groq OpenAI-compatible client ───────────────────
    # Groq exposes an OpenAI-compatible endpoint so we can use
    # the same openai Python library — just swap base_url and key.
    client = OpenAI(
        base_url=GROQ_BASE_URL,
        api_key=os.environ["GROQ_API_KEY"],
    )

    # ── Main ReAct Loop ────────────────────────────────────────
    for step in range(1, max_steps + 1):
        print(f"\n{'─'*55}")
        print(f"  STEP {step}")
        print(f"{'─'*55}")

        # ── 1. THINK: Send context to Llama via Groq ──────────
        messages = _build_messages(filepath, conversation)
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            max_tokens=512,
            temperature=0.1,   # Low temperature → more deterministic/structured output
        )
        llm_output = response.choices[0].message.content.strip()

        # ── 2. Parse the LLM response ─────────────────────────
        thought = _parse_thought(llm_output)
        tool_name, argument = _parse_action(llm_output)

        print(f"  💭 Thought   : {thought}")
        print(f"  ⚡ Action    : {tool_name}({argument or ''})")

        # ── 3. Termination check ───────────────────────────────
        if tool_name == "FINISH" or tool_name is None:
            print("\n✅ Agent decided it has enough information. Finishing loop.")
            break

        # ── 4. Duplicate action guard ──────────────────────────
        action_key = f"{tool_name}({argument})"
        if action_key in seen_actions:
            observation = f"Skipped: {action_key} was already executed."
            print(f"  ⚠️  {observation}")
        else:
            seen_actions.add(action_key)

            # ── 5. ACT: Run the selected tool ──────────────────
            if tool_name not in TOOLS:
                observation = f"Error: Unknown tool '{tool_name}'."
            else:
                try:
                    func = TOOLS[tool_name]
                    # Call with or without an argument
                    if argument:
                        observation = func(argument)
                    else:
                        observation = func()
                except Exception as e:
                    observation = f"Tool error: {str(e)}"

        # ── 6. OBSERVE: Log the result ─────────────────────────
        print(f"  📊 Observation:\n")
        for line in str(observation).split("\n"):
            print(f"       {line}")

        # ── 7. Update conversation history ────────────────────
        # This is what gets passed back to the LLM next turn.
        conversation.append(
            f"Thought: {thought}\n"
            f"Action: {action_key}\n"
            f"Observation: {observation}"
        )

        # Keep clean dict-based history for the report generator
        history.append({
            "thought":     thought,
            "action":      action_key,
            "observation": str(observation),
        })

    print(f"\n{'='*60}")
    print(f"  🏁 Loop complete after {len(history)} steps.")
    print(f"{'='*60}\n")

    return history
