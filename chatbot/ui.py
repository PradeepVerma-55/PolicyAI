"""
ui.py — Gradio layout and event wiring for PolicyAI Chatbot

Exports
-------
demo : gr.Blocks instance — passed to demo.launch() in app.py.
"""

import gradio as gr

from handlers import respond, clear_chat

SAMPLE_QUESTIONS = [
    "What are the leave entitlements for employees?",
    "What are the password and authentication requirements?",
    "How should a security incident be reported and handled?",
    "What security measures are required for remote work?",
    "What are the disciplinary action procedures?",
    "How should employees be trained on IT security awareness?",
]

# ── Layout ─────────────────────────────────────────────────────────────────────
with gr.Blocks(title="PolicyAI — HR & IT Security Intelligence") as demo:

    # ── Header ─────────────────────────────────────────────────────────────────
    gr.HTML("""
    <div id="policyai-header">
        <div class="header-logo">
            <span class="logo-icon">&#128272;</span>
            <span class="logo-text">PolicyAI</span>
        </div>
        <p class="header-sub">
            AI-powered HR &amp; IT Security policy intelligence &mdash; instant answers grounded in
            your HR policies, NIST Cybersecurity Framework, incident response guides,
            and remote work security documents, with exact page citations.
        </p>
        <div class="badge-row">
            <span class="badge badge-b">&#9889; Groq &middot; llama-3.1-8b</span>
            <span class="badge badge-g">&#10003; Zero hallucination</span>
            <span class="badge badge-v">&#128196; Page-level citations</span>
            <span class="badge badge-o">&#128196; 5 Policy Sources</span>
        </div>
    </div>
    """)

    # ── Main two-column layout ──────────────────────────────────────────────────
    with gr.Row(equal_height=False):

        # ── Left — chat interface ───────────────────────────────────────────
        with gr.Column(scale=63):

            chatbot = gr.Chatbot(
                value=[],
                height=500,
                show_label=False,
                layout="bubble",
                elem_id="policyai-chat",
                placeholder=(
                    "<div style='text-align:center;padding:70px 20px;'>"
                    "<div style='font-size:44px;margin-bottom:14px;'>&#128272;</div>"
                    "<div style='font-size:15px;font-weight:600;color:#2a3f5a;'>"
                    "Ask PolicyAI anything</div>"
                    "<div style='font-size:13px;margin-top:8px;color:#1e2f42;'>"
                    "HR policies, IT security standards, incident response, remote work &mdash; "
                    "select a quick question or type your own.</div>"
                    "</div>"
                ),
            )

            with gr.Row(elem_id="policyai-input-row"):
                msg_input = gr.Textbox(
                    placeholder="Ask a policy question…",
                    show_label=False,
                    scale=6,
                    autofocus=True,
                    lines=1,
                    max_lines=5,
                    container=False,
                    elem_id="policyai-msg",
                )
                send_btn = gr.Button(
                    "Send ➤",
                    variant="primary",
                    scale=1,
                    min_width=78,
                    elem_id="policyai-send",
                )
                clear_btn = gr.Button(
                    "✕ Clear",
                    variant="secondary",
                    scale=1,
                    min_width=72,
                    elem_id="policyai-clear",
                )

        # ── Right — quick questions + sources ───────────────────────────────
        with gr.Column(scale=37, min_width=260):

            # Quick questions card
            gr.HTML("""
            <div class="panel-section">
                <div class="panel-title">&#128161; &nbsp;Quick Questions</div>
                <div class="panel-body">
            """)
            for q in SAMPLE_QUESTIONS:
                gr.Button(q, variant="secondary", size="sm", elem_classes="q-btn").click(
                    fn=lambda question=q: question,
                    outputs=msg_input,
                )
            gr.HTML("</div></div>")

            # Sources card
            gr.HTML("""
            <div class="panel-section" style="margin-top:12px;">
                <div class="panel-title">&#128196; &nbsp;Retrieved Sources</div>
            """)
            sources_box = gr.Textbox(
                value="",
                placeholder="Source chunks will appear here after your first question...",
                interactive=False,
                lines=13,
                max_lines=22,
                show_label=False,
                container=False,
                elem_id="policyai-sources",
            )
            gr.HTML("</div>")

    # ── Footer ──────────────────────────────────────────────────────────────────
    gr.HTML("""
    <div id="policyai-footer">
        Powered by
        <a href="https://groq.com" target="_blank">Groq</a>
        <span class="sep">&middot;</span>
        <a href="https://qdrant.tech" target="_blank">Qdrant</a>
        <span class="sep">&middot;</span>
        <a href="https://python.langchain.com" target="_blank">LangChain</a>
        <span class="sep">&middot;</span>
        <a href="https://gradio.app" target="_blank">Gradio</a>
        <span class="sep">|</span>
        Codebasics AI Engineering Bootcamp
    </div>
    """)

    # ── Event wiring ────────────────────────────────────────────────────────────
    send_btn.click(
        fn=respond,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, sources_box],
    ).then(fn=lambda: "", outputs=msg_input)

    msg_input.submit(
        fn=respond,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, sources_box],
    ).then(fn=lambda: "", outputs=msg_input)

    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot, msg_input, sources_box],
    )
