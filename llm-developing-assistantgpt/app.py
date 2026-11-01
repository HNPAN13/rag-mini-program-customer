import sys
import gradio as gr
import pandas as pd
from AssistantGPT import AssistantGPT
from config import DEFAULT_MODEL, MODEL_TO_MAX_TOKENS, MODELS, DEFAULT_MAX_TOKENS
from file_processor_helper import FileProcessorHelper
from loguru import logger
from utils import build_chat_document_prompt, upload_files

logger.remove()
logger.add(sys.stderr, level="DEBUG")


def fn_update_max_tokens(model, origin_set_tokens):
    new_max_tokens = MODEL_TO_MAX_TOKENS.get(model)
    new_max_tokens = new_max_tokens if new_max_tokens else origin_set_tokens

    new_set_tokens = origin_set_tokens if origin_set_tokens <= new_max_tokens else DEFAULT_MAX_TOKENS

    new_max_tokens_component = gr.Slider(
        minimum=0,
        maximum=new_max_tokens,
        value=new_set_tokens,
        step=1.0,
        label="max_tokens",
        interactive=True,
    )
    return new_max_tokens_component


def fn_chat(
        chat_mode,
        uploaded_file_paths_df,
        user_input,
        chat_history,
        model,
        max_tokens,
        temperature,
        stream,
        top_n
):
    logger.info(f"组件输入 | user_input: {user_input} chat_history: {chat_history}")
    chat_history = [] if not chat_history else chat_history

    if not user_input:
        gr.Warning("请输入您的问题")
        logger.warning("请输入您的问题")
        yield chat_history
        return

    uploaded_file_paths = uploaded_file_paths_df['已上传的文件'].values.tolist()

    logger.info(f"\n"
                f"问答模式: {chat_mode} \n"
                f"文件路径: {uploaded_file_paths} {type(uploaded_file_paths)} \n"
                f"用户输入: {user_input} \n"
                f"历史记录: {chat_history} \n"
                f"使用模型: {model} {type(model)}\n"
                f"要生成的最大token数: {max_tokens} {type(max_tokens)}\n"
                f"温度: {temperature} {type(temperature)}\n"
                f"是否流式输出: {stream} {type(stream)}\n"
                f"top_n: {top_n} {type(top_n)}")

    messages = []
    if chat_mode == "普通问答":
        messages = []
        for msg in chat_history:
            role = msg.get("role")
            content = msg.get("content")
            if role in ("user", "assistant") and content is not None:
                messages.append({"role": role, "content": content})
        # 把当前用户提问加入消息
        messages.append({"role": "user", "content": user_input})
    else:
        # 文档问答
        if not isinstance(uploaded_file_paths, list) or not uploaded_file_paths or '' in uploaded_file_paths:
            gr.Warning("未上传文件")
            yield chat_history
            return

        user_prompt = build_chat_document_prompt(
            uploaded_file_paths, user_input, chat_history, top_n)
        if user_prompt:
            messages.append({"role": "user", "content": user_prompt})
        else:
            logger.error("生成 user_prompt 失败")
            messages = []

    if not messages:
        logger.error(f"messages为空列表")
        gr.Warning("服务器错误")
        yield chat_history
        return
    else:
        logger.trace(f"messages: {messages}")
        gpt = AssistantGPT()
        bot_response = gpt.get_completion(
            messages, model, max_tokens, temperature, stream)
        if stream:
            reply_buf = ""
            for character in bot_response:
                character_content = character.choices[0].delta.content
                if character_content is not None:
                    reply_buf += character_content
                    # 关键：每次都生成一份全新历史，最后一条是用户+当前累计回答
                    tmp_history = chat_history.copy()
                    tmp_history.append({"role": "user", "content": user_input})
                    tmp_history.append({"role": "assistant", "content": reply_buf})
                    yield tmp_history
                else:
                    logger.success(f"流式输出 | bot_response: {reply_buf}")
                    prompt = ""
                    for message in messages:
                        prompt += message['content'] + "\n"
                    logger.trace(f"prompt: {prompt}")
                    prompt_tokens = FileProcessorHelper.tiktoken_len(prompt)
                    completion_tokens = FileProcessorHelper.tiktoken_len(reply_buf)
                    total_tokens = prompt_tokens + completion_tokens
                    logger.success(f"流式输出 | total_tokens: {total_tokens} "
                                   f"= prompt_tokens:{prompt_tokens} + completion_tokens: {completion_tokens}")
        else:
            reply_buf = bot_response
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": reply_buf})
            logger.success(f"非流式输出 | bot_response: {reply_buf}")
            yield chat_history



def fn_upload_files(unuploaded_file_paths):
    logger.trace(f"组件输入 | unuploaded_file_paths: {unuploaded_file_paths}")
    uploaded_file_paths = []
    for file_path in unuploaded_file_paths:
        result = upload_files(str(file_path))
        if result.get('code') == 200:
            gr.Info("文件上传成功！")
            uploaded_file_paths.append(
                result.get('data').get('uploaded_file_path'))
        else:
            raise gr.Error("文件上传失败！")
    return pd.DataFrame({'已上传的文件': uploaded_file_paths})


with gr.Blocks() as demo:
    gr.Markdown("# <center>AssistantGPT</center>")
    with gr.Row(equal_height=True):
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(label="聊天机器人")
            user_input_textbox = gr.Textbox(label="用户输入框", value="这篇文章讲了什么？")
            with gr.Row():
                submit_btn = gr.Button("Submit")
                clear_btn = gr.Button("Clear")
        with gr.Column(scale=1):
            with gr.Tab(label="问答"):
                chat_mode_radio = gr.Radio(
                    choices=[
                        "普通问答",
                        "文档问答"],
                    label="问答模式",
                    value="文档问答",
                    interactive=True)
                file_paths_files = gr.Files(
                    label="上传文件",
                    file_count="multiple",
                    file_types=[".pdf", ".txt"],
                    type="filepath",
                )
                file_paths_dataframe = gr.Dataframe(
                    value=pd.DataFrame({'已上传的文件': []}))
                top_n_number = gr.Number(label="top_n", value=20)
            with gr.Tab(label="模型参数"):
                with gr.Column():
                    model_dropdown = gr.Dropdown(
                        label="model",
                        choices=MODELS,
                        value=DEFAULT_MODEL,
                        multiselect=False,
                        interactive=True,
                    )
                    max_tokens_slider = gr.Slider(
                        minimum=0,
                        maximum=4096,
                        value=1000,
                        step=1.0,
                        label="max_tokens",
                        interactive=True)
                    temperature_slider = gr.Slider(
                        minimum=0,
                        maximum=1,
                        value=0.7,
                        step=0.01,
                        label="temperature",
                        interactive=True)
                    stream_radio = gr.Radio(
                        choices=[True, False],
                        label="stream",
                        value=True,
                        interactive=True)

    model_dropdown.change(
        fn=fn_update_max_tokens,
        inputs=[model_dropdown, max_tokens_slider],
        outputs=max_tokens_slider
    )

    # ========= 这里直接绑定 fn_chat，没有 then =========
    user_input_textbox.submit(
        fn=fn_chat,
        inputs=[
            chat_mode_radio,
            file_paths_dataframe,
            user_input_textbox,
            chatbot,
            model_dropdown,
            max_tokens_slider,
            temperature_slider,
            stream_radio,
            top_n_number
        ],
        outputs=[chatbot]
    )

    submit_btn.click(
        fn=fn_chat,
        inputs=[
            chat_mode_radio,
            file_paths_dataframe,
            user_input_textbox,
            chatbot,
            model_dropdown,
            max_tokens_slider,
            temperature_slider,
            stream_radio,
            top_n_number
        ],
        outputs=[chatbot]
    )

    clear_btn.click(lambda: None, None, chatbot, queue=False)

    file_paths_files.upload(
        fn=fn_upload_files,
        inputs=[file_paths_files],
        outputs=[file_paths_dataframe],
        show_progress=True,
    )

demo.queue().launch()
