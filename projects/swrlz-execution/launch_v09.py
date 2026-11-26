"""Preserve v0.7/v0.8 endpoints and add authenticated fixed browser-in-VM test."""
import os
import gradio as gr
from launch_v08 import demo
from vm_browser_v09 import remote
with demo:
    raw=gr.Textbox(visible=False)
    sig=gr.Textbox(visible=False)
    result=gr.JSON(visible=False)
    button=gr.Button(visible=False)
    button.click(remote,inputs=[raw,sig],outputs=result,api_name="swrlz_vm_browser_v09",concurrency_limit=1)
if __name__=="__main__":
    demo.queue(max_size=4).launch(server_name="0.0.0.0",server_port=int(os.getenv("PORT","7860")))
