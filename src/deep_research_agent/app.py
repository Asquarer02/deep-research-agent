import gradio as gr
from dotenv import load_dotenv

from .research_manager import ResearchManager


async def get_clarifying_questions(query: str):
    """Phase 1: generate clarifying questions and reveal the answers step.

    Outputs: [questions_output, questions_group, answers_group]
    """
    if not query.strip():
        yield "⚠️ Please enter a research topic first.", gr.update(visible=True), gr.update(visible=False)
        return

    async for kind, payload in ResearchManager().run(query):
        if kind == "status":
            yield f"_{payload}_", gr.update(visible=True), gr.update(visible=False)
        elif kind == "questions":
            yield payload, gr.update(visible=True), gr.update(visible=True)


async def do_research(query: str, clarification_answers: str):
    """Phase 2: run the pipeline, streaming progress separately from the report.

    Outputs: [status_output, report_output, report_group]
    """
    if not clarification_answers.strip():
        yield "⚠️ Please answer the clarifying questions above first.", gr.update(), gr.update(visible=True)
        return

    async for kind, payload in ResearchManager().run(query, clarification_answers):
        if kind == "status":
            yield f"⏳ {payload}", gr.update(), gr.update(visible=True)
        elif kind == "report":
            yield "✅ Research complete.", payload, gr.update(visible=True)


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Deep Research") as ui:
        gr.Markdown("# 🔍 Deep Research")
        gr.Markdown(
            "Enter a topic, answer a few clarifying questions, and get a comprehensive, "
            "AI-researched report."
        )

        # Step 1 — always visible
        with gr.Group():
            gr.Markdown("### 1&nbsp;&nbsp;·&nbsp;&nbsp;Your research topic")
            query_textbox = gr.Textbox(
                show_label=False,
                placeholder="e.g. The impact of the USA–Iran war on Pakistan's economy",
                lines=2,
            )
            get_questions_button = gr.Button("Get clarifying questions →", variant="primary")

        # Step 2 — revealed once questions are generated
        with gr.Group(visible=False) as questions_group:
            gr.Markdown("### 2&nbsp;&nbsp;·&nbsp;&nbsp;Clarifying questions")
            questions_output = gr.Markdown()

        # Step 3 — revealed alongside the questions
        with gr.Group(visible=False) as answers_group:
            gr.Markdown("### 3&nbsp;&nbsp;·&nbsp;&nbsp;Your answers")
            clarification_answers = gr.Textbox(
                show_label=False,
                placeholder="Answer the questions above — e.g.\n1) overall impact\n2) both\n3) 2026 to now",
                lines=4,
            )
            do_research_button = gr.Button("Start research →", variant="primary")

        # Step 4 — revealed when research starts; progress and report are separate
        with gr.Group(visible=False) as report_group:
            gr.Markdown("### 4&nbsp;&nbsp;·&nbsp;&nbsp;Research report")
            status_output = gr.Markdown()
            report_output = gr.Markdown()

        get_questions_button.click(
            fn=get_clarifying_questions,
            inputs=query_textbox,
            outputs=[questions_output, questions_group, answers_group],
        )
        query_textbox.submit(
            fn=get_clarifying_questions,
            inputs=query_textbox,
            outputs=[questions_output, questions_group, answers_group],
        )
        do_research_button.click(
            fn=do_research,
            inputs=[query_textbox, clarification_answers],
            outputs=[status_output, report_output, report_group],
        )
    return ui


def main() -> None:
    load_dotenv(override=True)
    build_ui().launch(inbrowser=True, theme=gr.themes.Soft(primary_hue="sky"))


if __name__ == "__main__":
    main()
