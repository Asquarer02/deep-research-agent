# Deep Research Agent

A multi-agent **deep research assistant** with a [Gradio](https://www.gradio.app/) web UI, built on the
[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/). Give it a topic and it first asks a
few clarifying questions to sharpen the request, then plans targeted web searches, runs them in parallel,
synthesizes a long-form markdown report, and emails the result to you.

## How it works

The app runs as a **two-step flow**. First you enter a query and the `ClarifyAgent` generates three
clarifying questions. You answer them, and those answers feed the rest of the pipeline so the research
stays focused on what you actually want.

The pipeline is orchestrated by `ResearchManager`, which coordinates five specialized agents:

```
  query ───▶ ┌──────────────┐
             │ ClarifyAgent │  asks 3 clarifying questions
             └──────┬───────┘
                    │  ← user answers the questions
                    ▼
             ┌──────────────┐
             │ PlannerAgent │  plans targeted searches from query + answers
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
| `ClarifyAgent` | `clarify_agent.py` | Generates clarifying questions to narrow the query |
| `PlannerAgent` | `planner_agent.py` | Turns the query + answers into a structured search plan |
| `Search agent` | `search_agent.py` | Searches the web and summarizes each result |
| `WriterAgent`  | `writer_agent.py`  | Writes a cohesive, long-form markdown report |
| `Email agent`  | `email_agent.py`   | Formats and sends the report as an HTML email |

Progress updates stream back to the Gradio UI live as each stage completes. The email step is
non-fatal — if SendGrid isn't configured (or is out of credits), the report is still displayed.

## Project structure

```
deep_research_agent/
├── src/deep_research_agent/
│   ├── app.py               # Gradio UI (two-step flow) + entry point (main)
│   ├── research_manager.py  # Orchestrates the agent pipeline
│   ├── clarify_agent.py
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
   | `OPENAI_API_KEY` | ✅ | Powers all five agents |
   | `SENDGRID_API_KEY` | ⬜ | Sending the report email |
   | `MAIL_FROM_EMAIL` | ⬜ | Verified SendGrid sender address |
   | `MAIL_TO_EMAIL` | ⬜ | Where the report is emailed |

## Running

```bash
uv run deep-research
```

This launches the Gradio app and opens it in your browser (default: <http://127.0.0.1:7860>).
Then:

1. **Step 1** — enter your topic and click **Get clarifying questions**.
2. **Step 2** — the app shows three clarifying questions; type your answers.
3. **Step 3** — click **Start research** and watch the report build in real time.

> **Note:** Each run makes paid OpenAI API calls. If you haven't configured SendGrid, the research
> and report steps still work — only the final email step is skipped (the report still displays).

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
