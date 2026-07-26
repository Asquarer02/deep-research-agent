from agents import Runner, trace, gen_trace_id
from .clarify_agent import clarify_agent, ClarificationQuestions
from .planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from .search_agent import search_agent
from .writer_agent import writer_agent, ReportData
from .email_agent import email_agent
import asyncio


class ResearchManager:

    async def run(self, query: str, clarification_answers: str | None = None):
        """ Run the deep research process, yielding ``(kind, payload)`` events.

        ``kind`` is one of ``"status"`` (a short progress line), ``"questions"``
        (the clarifying-questions markdown) or ``"report"`` (the final report).
        The UI routes each kind to a different place, so progress never mixes
        into the report.

        Two phases:
        - ``run(query)`` (no answers) -> emit clarifying questions, then stop.
        - ``run(query, answers)`` -> plan, search, write the report, and email it.
        """
        trace_id = gen_trace_id()
        with trace("Deep research trace", trace_id=trace_id):
            # Trace URL is developer info -> console only, kept out of the UI.
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")

            # Phase 1: no answers yet -> ask clarifying questions and wait for the user.
            if clarification_answers is None:
                yield ("status", "Generating clarifying questions...")
                clarifications = await self.clarify(query)
                questions_md = "\n".join(
                    f"{i}. {q}" for i, q in enumerate(clarifications.questions, 1)
                )
                questions_md += f"\n\n> 💡 *{clarifications.reasoning}*"
                yield ("questions", questions_md)
                return

            # Phase 2: answers provided -> run the full research pipeline.
            yield ("status", "Planning targeted searches...")
            search_plan = await self.plan_searches(query, clarification_answers)

            yield ("status", f"Searching the web ({len(search_plan.searches)} queries)...")
            search_results = await self.perform_searches(search_plan)

            yield ("status", "Synthesizing the report...")
            report = await self.write_report(query, clarification_answers, search_results)

            yield ("status", "Sending email...")
            email_status = await self.send_email(report)

            yield ("status", email_status)
            yield ("report", report.markdown_report)

    async def clarify(self, query: str) -> ClarificationQuestions:
        """ Generate clarifying questions for the query """
        print("Generating clarifying questions...")
        result = await Runner.run(clarify_agent, f"Original query: {query}")
        return result.final_output_as(ClarificationQuestions)

    async def plan_searches(self, query: str, clarification_answers: str) -> WebSearchPlan:
        """ Plan the searches to perform, informed by the clarification answers """
        print("Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Original query: {query}\n\nClarifying questions and answers:\n{clarification_answers}",
        )
        plan = result.final_output_as(WebSearchPlan)
        print(f"Will perform {len(plan.searches)} searches")
        return plan

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """ Perform the planned searches in parallel """
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """ Perform a single web search """
        input = (
            f"Search query: {item.query}\n"
            f"Reason: {item.reason}\n"
            f"Expected focus: {item.expected_focus}"
        )
        try:
            result = await Runner.run(search_agent, input)
            return str(result.final_output)
        except Exception:
            return None

    async def write_report(self, query: str, clarification_answers: str, search_results: list[str]) -> ReportData:
        """ Synthesize the search results into a report """
        print("Thinking about report...")
        input = (
            f"Original query: {query}\n\n"
            f"Clarifying questions and answers:\n{clarification_answers}\n\n"
            f"Search results:\n" + "\n".join(search_results)
        )
        result = await Runner.run(writer_agent, input)
        print("Finished writing report")
        return result.final_output_as(ReportData)

    async def send_email(self, report: ReportData) -> str:
        """ Email the report. Failures are non-fatal so the report still displays. """
        print("Writing email...")
        try:
            await Runner.run(email_agent, report.markdown_report)
            print("Email sent")
            return "Email sent, research complete."
        except Exception as exc:  # e.g. SendGrid not configured or out of credits
            print(f"Email step failed: {exc}")
            return f"Research complete (email step skipped: {exc})."
