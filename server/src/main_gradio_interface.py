import gradio as gr
from farm_agent import ask_farm_agent

# Create the Gradio interface
with gr.Blocks(title="Farm Data Agent") as demo:
    gr.Markdown("""
    # 🧑‍🌾 Ask the Farm Agent!
    Ask questions about your farm data: profits, harvests, efficiency, and more.
    """)

    with gr.Row():
        with gr.Column():
            question = gr.Textbox(
                label="What would you like to know?",
                placeholder="e.g., Which crop had the highest profit?",
                lines=3
            )
            with gr.Row():
                submit_btn = gr.Button("Ask")

        with gr.Column():
            response = gr.Textbox(
                label="Response",
                lines=10,
                show_copy_button=True
            )

    # Set up Gradio interactions
    submit_btn.click(
        fn=ask_farm_agent,
        inputs=question,
        outputs=response
    )

    question.submit(
        fn=ask_farm_agent,
        inputs=question,
        outputs=response
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()
    