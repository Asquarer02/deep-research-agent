import gradio as gr
from dotenv import load_dotenv

from .research_manager import ResearchManager


async def get_clarifying_questions(query: str):
    """Phase 1: generate clarifying questions for the query (streams progress)."""
    text = ""
    async for chunk in ResearchManager().run(query):
        text += chunk + "\n"
        yield text


async def do_research(query: str, clarification_answers: str):
    """Phase 2: run the full research pipeline with the user's answers."""
    async for chunk in ResearchManager().run(query, clarification_answers):
        yield chunk


def build_ui() -> gr.Blocks:
    with gr.Blocks() as ui:
        gr.Markdown("# 🔍 Deep Research")
        gr.Markdown(
            "Enter a topic, answer a few clarifying questions, and get a comprehensive, "
            "AI-researched report."
        )

        with gr.Group():
            gr.Markdown("### Step 1 — Your research query")
            query_textbox = gr.Textbox(
                label="What topic would you like to research?",
                placeholder="e.g. The impact of remote work on urban housing markets",
                lines=2,
            )
            get_questions_button = gr.Button("Get clarifying questions", variant="primary")

        with gr.Group():
            gr.Markdown("### Step 2 — Clarifying questions")
            questions_output = gr.Markdown()

        with gr.Group():
            gr.Markdown("### Step 3 — Your answers")
            clarification_answers = gr.Textbox(
                label="Answer the clarifying questions",
                placeholder="Type your answers here...",
                lines=4,
            )
            do_research_button = gr.Button("Start research", variant="primary")

        with gr.Group():
            gr.Markdown("### Step 4 — Research report")
            report = gr.Markdown()

        get_questions_button.click(fn=get_clarifying_questions, inputs=query_textbox, outputs=questions_output)
        query_textbox.submit(fn=get_clarifying_questions, inputs=query_textbox, outputs=questions_output)
        do_research_button.click(fn=do_research, inputs=[query_textbox, clarification_answers], outputs=report)
    return ui


def main() -> None:
    load_dotenv(override=True)
    build_ui().launch(inbrowser=True, theme=gr.themes.Soft(primary_hue="sky"))


if __name__ == "__main__":
    main()
