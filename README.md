# 🤖 AI Data Analysis Agent

> A from-scratch implementation of the **ReAct (Reasoning + Acting)** agentic AI pattern — built to autonomously explore any CSV dataset, uncover insights, and produce a professional Markdown report.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Model](https://img.shields.io/badge/LLM-Llama--3.1--8B-orange?logo=meta)](https://groq.com)
[![Powered by](https://img.shields.io/badge/Powered%20by-Groq-purple)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 What Is This?

This project is a **fully autonomous AI agent** that acts like a data analyst. You hand it a CSV file, and it:

1. **Thinks** about what to analyse next (via Llama-3.1-8B-Instruct)
2. **Acts** by calling one of 7 Python analysis tools
3. **Observes** the result and feeds it back into its memory
4. **Repeats** until it has enough insights to write a report
5. **Writes** a structured Markdown report with all findings

No hardcoded analysis steps. No fixed rules about what to check. The LLM decides — autonomously.

---

## 🧠 Agentic AI Concepts Demonstrated

This project is designed to teach the **5 foundational concepts** of agentic AI:

| # | Concept | What It Means | Where to See It |
|---|---------|---------------|-----------------|
| 1 | **ReAct Loop** | Think → Act → Observe → Repeat | `agent.py` → `run_agent()` |
| 2 | **Tool Use** | LLM picks Python functions to call | `tools.py` + `TOOLS` registry |
| 3 | **Autonomous Planning** | Agent decides what to analyse next | LLM's `Thought:` step |
| 4 | **Memory via Context** | Full history re-sent each iteration | `conversation` list in `agent.py` |
| 5 | **Termination** | Agent signals when it's done | `FINISH` action |

### The ReAct Loop — Visualised

```
┌─────────────────────────────────────────────────────┐
│                    ReAct Loop                        │
│                                                      │
│  ┌─────────┐    ┌────────┐    ┌──────────────────┐  │
│  │  THINK  │───▶│  ACT   │───▶│    OBSERVE       │  │
│  │  (LLM)  │    │(Python)│    │  (tool result)   │  │
│  └─────────┘    └────────┘    └──────────────────┘  │
│       ▲                               │             │
│       └───────────────────────────────┘             │
│                  (repeat)                           │
└─────────────────────────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
data_analysis_agent/
│
├── main.py              ← START HERE — orchestrates everything
├── agent.py             ← The Brain (ReAct loop + LLM calls)
├── tools.py             ← The Hands (7 Python analysis tools)
├── report.py            ← The Voice (generates Markdown report)
│
├── data/
│   └── sample_sales.csv ← Built-in test dataset (100 rows)
│
├── output/              ← Agent writes reports + charts here
│   ├── report.md        ← Auto-generated analysis report
│   └── hist_*.png       ← Auto-generated histogram charts
│
├── requirements.txt     ← Python dependencies
├── .env.example         ← API key template (copy → .env)
└── COMPONENTS.md        ← Deep-dive guide to every file
```

---

## 🛠️ The 7 Analysis Tools

The agent autonomously chooses from these tools during each step:

| Tool | What It Does |
|------|-------------|
| `load_data(filepath)` | Loads a CSV file — always called first |
| `describe_data()` | Reports shape, column types, and missing values |
| `compute_stats(column)` | Mean, median, std dev, min, max, skewness |
| `find_correlations()` | Top correlation pairs across numeric columns |
| `plot_histogram(column)` | Saves a distribution chart as a PNG |
| `detect_outliers(column)` | IQR-based anomaly detection |
| `value_counts(column)` | Frequency table for categorical columns |
| `FINISH` | Signals the agent is done — triggers report generation |

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/data_analysis_agent.git
cd data_analysis_agent
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get a Free Groq API Key

The agent uses **Meta's Llama-3.1-8B-Instruct**, served for free by [Groq](https://groq.com) — the fastest free LLM inference available, no credit card required.

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up / Log in → **API Keys** → **Create API Key**
3. Copy your key (starts with `gsk_...`)

### 5. Configure Your API Key

```bash
cp .env.example .env
```

Open `.env` and paste your key:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

> ⚠️ **Never commit `.env` to Git.** It's already in `.gitignore`.

### 6. Run the Agent

```bash
# Use the built-in sample dataset
python main.py

# Or pass your own CSV
python main.py data/your_file.csv
```

---

## 📊 Example Output

When you run the agent, you'll see the live ReAct loop in your terminal:

```
📂  Dataset  : data/sample_sales.csv
🦙  Model    : Llama-3.1-8B-Instruct
⚡  Provider : Groq (free tier)
📁  Output   : ./output/

════════════════════════════════════════════════════════════
  🤖  AI DATA ANALYSIS AGENT  —  Starting ReAct Loop
════════════════════════════════════════════════════════════

───────────────────────────────────────────────────────────
  STEP 1
───────────────────────────────────────────────────────────
  💭 Thought   : I should load the data first to understand it.
  ⚡ Action    : load_data(data/sample_sales.csv)
  📊 Observation:
       Data loaded successfully!
         Shape  : 100 rows × 6 columns
         Columns: date, region, product, units_sold, revenue, discount

  STEP 2
  💭 Thought   : Let me describe the dataset structure.
  ⚡ Action    : describe_data()
  ...

✅ Agent decided it has enough information. Finishing loop.

📝  Generating final report...
📁  Saved: output/report.md
📊  Charts: hist_revenue.png, hist_units_sold.png

✅  Done! Your analysis is complete.
```

The agent saves a **full Markdown report** (`output/report.md`) and **histogram charts** (`output/hist_*.png`) automatically.

---

## 📄 Sample Report (auto-generated)

The final report follows a consistent 6-section structure:

```markdown
# Data Analysis Report: sample_sales.csv

## 1. Dataset Overview
## 2. Key Statistics
## 3. Correlation Insights
## 4. Outliers & Anomalies
## 5. Category Breakdown
## 6. Key Takeaways & Recommendations
```

---

## 🧩 How It Works — Under the Hood

### Step-by-Step Flow

```
main.py
  │
  ├─ load_dotenv()          ← Reads GROQ_API_KEY from .env
  ├─ run_agent(filepath)    ← Starts the ReAct loop in agent.py
  │     │
  │     ├─ THINK: Send full conversation history to Llama via Groq API
  │     ├─ PARSE: Extract Thought + Action using regex
  │     ├─ ACT:   Look up tool in TOOLS dict, run Python function
  │     ├─ OBSERVE: Append result to conversation history
  │     └─ REPEAT until LLM outputs FINISH or max_steps reached
  │
  └─ generate_report(history) ← Sends all observations to LLM to write report
```

### Why Memory Works This Way

LLMs have **no persistent memory** between API calls. The agent's "memory" is implemented by:
- Keeping a `conversation` list of all `Thought / Action / Observation` triples
- Re-sending the **entire history** on every LLM call
- This gives the LLM full context of what has been done so far

### Duplicate Action Guard

A `seen_actions` set prevents the agent from repeating the same tool call twice, ensuring the analysis always moves forward.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `openai` | ≥ 1.0.0 | Groq API client (OpenAI-compatible) |
| `pandas` | ≥ 2.0.0 | Data loading and manipulation |
| `matplotlib` | ≥ 3.7.0 | Histogram chart generation |
| `numpy` | ≥ 1.24.0 | Correlation and outlier calculations |
| `python-dotenv` | ≥ 1.0.0 | Secure `.env` API key loading |
| `tabulate` | ≥ 0.9.0 | Formatted table output |

---

## 🔧 Extending the Project

Once you're comfortable, try these enhancements:

- **Add more tools** — `group_by_region()`, `monthly_trend()`, `top_products()`
- **Streamlit UI** — Wrap it in a web interface with a CSV file uploader
- **Q&A mode** — After the report, let the user ask follow-up questions
- **Multi-dataset comparison** — Run the agent on two CSVs and compare findings
- **Automated alerts** — Send the report to Slack or email automatically
- **Swap the model** — Try `llama-3.3-70b-versatile` on Groq for richer reasoning

---

## 📚 Learn More

- [ReAct: Synergizing Reasoning and Acting in Language Models (paper)](https://arxiv.org/abs/2210.03629)
- [Groq API Documentation](https://console.groq.com/docs)
- [Meta Llama 3 Models](https://ai.meta.com/blog/meta-llama-3/)

---

## 📝 License

This project is open-source under the [MIT License](LICENSE).

---

## 🙋‍♀️ Author

Built by **Devashree Pawar** as a hands-on exploration of agentic AI fundamentals.

> *"The best way to understand how AI agents work is to build one from scratch."*

---

⭐ If you found this useful, consider giving the repo a star!
