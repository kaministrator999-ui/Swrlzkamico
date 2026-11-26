"""Launch existing §X unchanged, with one authenticated fixed capability probe."""
import os
import gradio as gr
from app import demo
from vm_capability_v08 import remote_vm_probe
with demo:
    raw=gr.Textbox(visible=False)
    signature=gr.Textbox(visible=False)
    result=gr.JSON(visible=False)
    button=gr.Button(visible=False)
    button.click(remote_vm_probe,inputs=[raw,signature],outputs=result,api_name="swrlz_vm_v08",concurrency_limit=1)
if __name__=="__main__":
    demo.queue(max_size=4).launch(server_name="0.0.0.0",server_port=int(os.getenv("PORT","7860")))
