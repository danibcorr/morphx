# Standard libraries
import logging
import tempfile
from pathlib import Path
from typing import Any
import os

# 3rd-party libraries
import streamlit as st
import torch
from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig

# Own modules
from morphx.utils import create_logger

# Page configuration
st.set_page_config(page_title="File OCR", layout="centered")
st.title("File OCR", anchor=False)


@st.cache_resource(show_spinner=True)
def load_ocr_model() -> tuple[Any, Any]:
    """
    Load the DeepSeek OCR model and tokenizer with 4-bit quantization.
    Returns both model and tokenizer.
    """
    model_name: str = 'deepseek-ai/DeepSeek-OCR'

    quantconfig = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModel.from_pretrained(
        model_name,
        trust_remote_code=True,
        use_safetensors=True,
        device_map="auto",
        quantization_config=quantconfig,
        torch_dtype=torch.float,
        do_sample=False,
        temperature=None,
    ).eval()

    return model, tokenizer


def get_selected_model(logger: logging.Logger) -> str:
    """
    Retrieve the conversion model selected in the interface.
    """
    if "file_ocr_model" not in st.session_state:
        st.session_state["file_ocr_model"] = "DeepSeekOCR"

    with st.container():
        st.subheader("Model Selection")
        selected_model = st.radio(
            label="Choose your file conversion model",
            options=["DeepSeekOCR"],
            index=0
        )

    if selected_model != st.session_state["file_ocr_model"]:
        logger.info(f"Model changed to: {selected_model}.")
        st.session_state["file_ocr_model"] = selected_model

    return st.session_state["file_ocr_model"]


def process_uploaded_file(file_uploaded, model: Any) -> str | None:
    """
    Convert an uploaded file to Markdown using the provided model.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_uploaded.name).suffix) as tmp_file:
        tmp_file.write(file_uploaded.getvalue())
        tmp_path = tmp_file.name

    result = model.convert(tmp_path)
    return result.text_content if hasattr(result, "text_content") else None


def display_file_uploader_section(model: Any, tokenizer: Any) -> None:
    """
    Render the file uploader section and display conversion results.
    """
    with st.container():
        file_uploaded = st.file_uploader("Upload file to convert to Markdown")
        path_input = st.text_input("Insert the complete path to folder")

        if file_uploaded is not None:
            converted_text = process_uploaded_file(file_uploaded, model)
            if converted_text:
                st.text_area(
                    label="Conversion result",
                    value=converted_text,
                    height=400,
                )

        if path_input:
            prompt = "<image>\nConvert the document to markdown."
            output_path = './content/outputs/'
            os.makedirs(output_path, exist_ok=True)
            dir_list = sorted(os.listdir(path_input))

            for i, file_name in enumerate(dir_list):
                st.text(f"Start File: {i}")
                file_path = os.path.join(path_input, file_name)

                # Run inference
                model.infer(
                    tokenizer,
                    prompt=prompt,
                    image_file=file_path,
                    output_path=output_path,
                    base_size=1024,
                    image_size=1024,
                    crop_mode=False,
                    save_results = True,
                    test_compress=True
                )

                # Read the most recent output file
                output_file = os.path.join(output_path, "result.mmd")
                with open(output_file, 'r', encoding='utf-8') as f:
                    result_text = f.read()

                st.text_area(
                    label=f"Conversion result: {file_name}",
                    value=result_text,
                    height=400
                )

                st.text(f"End File: {i}\n")


def main() -> None:
    """
    Run the file conversion interface.
    """
    logger = create_logger(
        logger_file_name="./logs/",
        logger_name="transcriptions_logs.log"
    )

    # Model selection
    selected_model_name = get_selected_model(logger=logger)
    model, tokenizer = load_ocr_model()

    # Display file uploader and handle conversion
    if model is not None:
        display_file_uploader_section(model=model, tokenizer=tokenizer)


if __name__ == "__main__":
    main()
