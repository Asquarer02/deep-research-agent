# Deep Research Agent

A multi-agent **deep research assistant** with a [Gradio](https://www.gradio.app/) web UI, built on the
[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/). Give it a topic and it plans a set of
web searches, runs them in parallel, synthesizes a long-form markdown report, and (optionally) emails the
result to you.

## How it works

The pipeline is orchestrated by `ResearchManager`, which coordinates four specialized agents:

```
             ┌──────────────┐
  query ───▶ │ PlannerAgent │  decides which 5 web searches to run
             └──────┬───────┘
                    │  WebSearchPlan
                    ▼
             ┌──────────────┐
             │ Search agent │  runs each search in parallel (WebSearchTool)
             └──────┬───────┘
                    │  summaries
                    ▼
             ┌──────────────┐
             │ WriterAgent  │  synthesizes a detailed markdown report
             └──────┬───────┘
                    │  ReportData
                    ▼
             ┌──────────────┐
             │  Email agent │  sends the report as HTML via SendGrid
             └──────────────┘
```

| Agent | File | Responsibility |
|-------|------|----------------|
| `PlannerAgent` | `planner_agent.py` | Turns the query into a structured plan of web searches |
| `Search agent` | `search_agent.py` | Searches the web and summarizes each result |
| `WriterAgent`  | `writer_agent.py`  | Writes a cohesive, long-form markdown report |
| `Email agent`  | `email_agent.py`   | Formats and sends the report as an HTML email |

Progress updates stream back to the Gradio UI live as each stage completes.

## Project structure

```
deep_research_agent/
├── src/deep_research_agent/
│   ├── app.py               # Gradio UI + entry point (main)
│   ├── research_manager.py  # Orchestrates the agent pipeline
│   ├── planner_agent.py
│   ├── search_agent.py
│   ├── writer_agent.py
│   └── email_agent.py
├── pyproject.toml           # Project metadata & dependencies
├── uv.lock                  # Pinned, reproducible dependency versions
├── requirements.txt         # Direct deps (for pip users)
├── .env.example             # Template for required secrets
└── README.md
```

## Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** (recommended) — `pip install uv` or see the install docs
- An **OpenAI API key** (required)
- A **SendGrid API key** (optional — only needed for the email step)

## Setup

1. **Clone and install dependencies**

   ```bash
   git clone https://github.com/<your-username>/deep_research_agent.git
   cd deep_research_agent
   uv sync
   ```

   `uv sync` creates a local `.venv` and installs everything from the lockfile.

2. **Configure secrets**

   Copy the example env file and fill in your values:

   ```bash
   cp .env.example .env
   ```

   | Variable | Required | Purpose |
   |----------|----------|---------|
   | `OPENAI_API_KEY` | ✅ | Powers all four agents |
   | `SENDGRID_API_KEY` | ⬜ | Sending the report email |
   | `MAIL_FROM_EMAIL` | ⬜ | Verified SendGrid sender address |
   | `MAIL_TO_EMAIL` | ⬜ | Where the report is emailed |

## Running

```bash
uv run deep-research
```

This launches the Gradio app and opens it in your browser (default: <http://127.0.0.1:7860>).
Enter a topic, hit **Run**, and watch the report build in real time.

> **Note:** Each run makes paid OpenAI API calls. If you haven't configured SendGrid, the research
> and report steps still work — only the final email step will fail.

### Alternative: pip

If you prefer plain pip instead of uv:

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python -m deep_research_agent.app
```

## Tech stack

- **[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)** — agent orchestration, tool calling, tracing
- **[Gradio](https://www.gradio.app/)** — the web interface
- **[Pydantic](https://docs.pydantic.dev/)** — structured, validated agent outputs
- **[SendGrid](https://sendgrid.com/)** — email delivery
- **[uv](https://docs.astral.sh/uv/)** — dependency management

## License

MIT
