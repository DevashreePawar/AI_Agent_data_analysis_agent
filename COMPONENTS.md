# 🤖 AI Data Analysis Agent — Component Guide

A complete breakdown of every file, function, and agentic concept in this project.

---

## 🗂️ Project Structure at a Glance

```
data_analysis_agent/
│
├── main.py              ← START HERE — runs everything
├── agent.py             ← The Brain (ReAct Loop)
├── tools.py             ← The Hands (Python functions)
├── report.py            ← The Voice (Markdown report)
│
├── data/
│   └── sample_sales.csv ← Test dataset (100 rows)
├── output/              ← Agent writes reports + charts here
│
├── requirements.txt     ← Python packages needed
└── .env                 ← Your secret API key (never commit this!)
```

---

## 🧠 Core Agentic AI Concepts

Before diving into the files, here are the 5 big ideas this project teaches:

| # | Concept | Simple Definition | Where You See It |
|---|---------|-------------------|-----------------|
| 1 | **Tool Use** | LLM picks Python functions to call | `tools.py` + `agent.py` |
| 2 | **ReAct Loop** | Think → Act → Observe → Repeat | `agent.py:run_agent()` |
| 3 | **Autonomous Planning** | Agent decides what to do next | LLM's Thought step |
| 4 | **Memory via Context** | Full history re-sent each turn | `conversation` list in `agent.py` |
| 5 | **Termination** | Agent signals when it's done | `FINISH` action |

---

## 📄 File 1: `main.py` — Entry Point

**Role:** The launch button. Wires everything together.

**What it does, step by step:**

```
1. Load .env file  →  Read GEMINI_API_KEY
2. Validate key    →  Print helpful error if missing
3. Configure SDK   →  genai.configure(api_key=...)
4. Accept CSV path →  From command line or use default
5. Run agent       →  agent.run_agent(filepath)
6. Run reporter    →  report.generate_report(history)
7. Print report    →  Show in terminal + save to output/
```

**Key concept taught:** 
> **Separation of concerns** — `main.py` only orchestrates. It doesn't do any analysis or LLM calls itself.

---

## 📄 File 2: `agent.py` — The Brain (ReAct Loop)

This is the most important file. It implements the **ReAct (Reason + Act)** pattern.

### The ReAct Loop Visualised

```
╔══════════════════════════════════════════╗
║           REACT LOOP (1 iteration)       ║
╠══════════════════════════════════════════╣
║                                          ║
║  [1] BUILD PROMPT                        ║
║      System prompt + full history        ║
║             │                            ║
║             ▼                            ║
║  [2] THINK (LLM Call)                   ║
║      Gemini reads context, decides       ║
║      what to do next                     ║
║             │                            ║
║             ▼ LLM outputs:              ║
║      Thought: "I should check revenue"  ║
║      Action: compute_stats(revenue)      ║
║             │                            ║
║  [3] PARSE  │                            ║
║      Extract tool name + arguments       ║
║             │                            ║
║             ▼                            ║
║  [4] ACT (Run Python function)          ║
║      TOOLS["compute_stats"]("revenue")  ║
║             │                            ║
║             ▼                            ║
║  [5] OBSERVE                             ║
║      result = "Mean: 15420, Std: 8230"  ║
║             │                            ║
║             ▼                            ║
║  [6] APPEND TO HISTORY                  ║
║      conversation.append(T + A + O)     ║
║             │                            ║
║             └──────── back to [1] ──────╝
```

### Key Functions in `agent.py`

#### `run_agent(filepath, max_steps=15)`
The main loop. Runs up to `max_steps` ReAct cycles.

| Variable | What It Stores |
|---|---|
| `conversation` | Full text history re-sent to LLM each turn |
| `history` | Structured dict list used by `report.py` |
| `seen_actions` | Set of already-run actions (prevents repeats) |

#### `_build_prompt(filepath, conversation)`
Assembles the full LLM prompt. Includes:
- System instructions (rules + available tools)
- Full conversation history (this IS the agent's memory!)
- A `"Thought:"` suffix to guide the LLM's next output

> **Why we resend the full history every time:** LLMs have no persistent memory. The "context window" is their only memory. By appending each T/A/O cycle to a growing list and re-sending it, the LLM always knows what was already done.

#### `_parse_action(text)`
Uses **regex** to extract the tool call from LLM output:
```
LLM says:   "Action: compute_stats(revenue)"
We extract: tool_name = "compute_stats", argument = "revenue"
```

#### `_parse_thought(text)`
Extracts the reasoning text before the Action line.

---

## 📄 File 3: `tools.py` — The Hands

Each function here is a **tool** the agent can use. The LLM doesn't run code — it outputs a text instruction, and we run the actual Python.

### The 7 Tools

| Tool | Type | What It Does |
|---|---|---|
| `load_data(filepath)` | I/O | Loads CSV into a pandas DataFrame |
| `describe_data()` | Exploration | Shape, dtypes, missing values |
| `compute_stats(column)` | Statistics | Mean, median, std, skewness |
| `find_correlations()` | Statistics | Top column-pair correlations |
| `plot_histogram(column)` | Visualisation | Saves chart as PNG |
| `detect_outliers(column)` | Quality | IQR-based anomaly detection |
| `value_counts(column)` | Exploration | Frequency table for categories |

### The Tool Registry

```python
TOOLS = {
    "load_data": load_data,
    "compute_stats": compute_stats,
    ...
}
```

This dictionary lets us look up and call any tool by name at runtime:
```python
func = TOOLS[tool_name]   # e.g. TOOLS["compute_stats"]
result = func(argument)    # compute_stats("revenue")
```

### How Outlier Detection Works (IQR Method)

```
Q1 = 25th percentile value
Q3 = 75th percentile value
IQR = Q3 - Q1

Lower fence = Q1 - (1.5 × IQR)
Upper fence = Q3 + (1.5 × IQR)

Any value outside [Lower fence, Upper fence] = OUTLIER
```

This is a standard statistical method — robust because it's based
on the middle 50% of data, not the extreme values.

---

## 📄 File 4: `report.py` — The Voice

After the loop ends, the agent's observations are raw data:
```
"Mean: 24000.50, Std: 41000.12 ..."
"Outliers in units_sold: [150]"
```

`report.py` sends all of this to Gemini and asks it to write a 
professional Markdown report with 6 structured sections.

**Key insight:** We use the LLM twice:
1. **In the loop** → to reason and pick tools (analytical)
2. **In the report** → to communicate findings (writing)

This separation of "doing" and "reporting" is a common pattern in production agents.

---

## 📄 File 5: `data/sample_sales.csv`

A 100-row synthetic sales dataset with these columns:

| Column | Type | Description |
|---|---|---|
| `date` | date | Transaction date |
| `region` | text | North / South / East / West |
| `product` | text | Laptop / Phone / Tablet / Headphones |
| `units_sold` | number | Units sold per transaction |
| `revenue` | number | Revenue (in USD) |
| `discount` | number | Discount rate applied (0.0–0.15) |

**Hidden challenge for the agent:** Row 100 has `units_sold = 150` — a deliberate outlier
10× higher than average. A good agent should catch this!

---

## 🔑 Environment & API Setup

### Why `.env` files?
Hardcoding API keys in source code is a major security risk — anyone who sees
your code can use your key and run up your bill. We use:
1. `.env` file — stores the real key locally (never committed to git)
2. `python-dotenv` — loads it into `os.environ` at runtime
3. `os.getenv("GEMINI_API_KEY")` — reads it safely

### Getting a Free Gemini API Key
1. Go to [https://aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API key"**
4. Copy the key
5. Paste it in your `.env` file:
   ```
   GEMINI_API_KEY=AIza...your_key_here
   ```

---

## ▶️ Running the Project

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your API key
cp .env.example .env
# Edit .env and paste your Gemini key

# 3. Run the agent
python main.py data/sample_sales.csv
```

**What you'll see in the terminal:**
```
📂  Dataset  : data/sample_sales.csv
🤖  Model    : Gemini 1.5 Flash

════════════════════════════════════════
  STEP 1
────────────────────────────────────────
  💭 Thought   : I should load the data first
  ⚡ Action    : load_data(data/sample_sales.csv)
  📊 Observation:
       Data loaded! 100 rows × 6 columns

  STEP 2
  💭 Thought   : Now I'll check the structure
  ⚡ Action    : describe_data()
  ...
```

---

## 🚀 Extending the Project

Once you're comfortable, try these enhancements:

1. **Ask follow-up questions** — Add a Q&A mode after the report
2. **More tools** — Add `group_by_region()`, `monthly_trend()`, `top_products()`
3. **Streamlit UI** — Wrap it in a web interface with file upload
4. **Multi-dataset comparison** — Run the agent on two CSVs and compare
5. **Slack/email alerts** — Agent sends report to a channel automatically
