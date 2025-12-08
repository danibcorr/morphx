# Standard libraries
import logging
import tempfile
from pathlib import Path
from typing import Any

# 3pps
import streamlit as st
from markitdown import MarkItDown

# Own modules
from morphx.configs import FILE_CONVERSION_MODELS
from morphx.utils import create_logger

# Page configuration
st.set_page_config(page_title="File Conversion", layout="centered")
st.title("File Conversion", anchor=False)


@st.cache_resource(show_spinner=True)
def load_conversion_model(model_name: str) -> Any:
    """
    Load a file conversion model based on a provided model name.

    This function retrieves an instance of a conversion model matching the
    given name. The loaded model is cached so subsequent calls reuse the
    same instance. If an unsupported model name is supplied, an error
    message is displayed and no model is loaded.

    Args:
        model_name: Name of the conversion model to load.

    Returns:
        Model instance matching the provided name or None when no
        compatible model is available.
    """

    match model_name:
        case "MarkItDown":
            return MarkItDown()
        case _:
            st.error("Model not available")
            return None


def get_selected_model(logger: logging.Logger) -> str:
    """
    Retrieve the conversion model selected in the interface.

    The chosen model is stored in the session state so it remains stable
    across interactions. A container with a header and a set of selectable
    options is displayed. When the user changes the selection, the update
    is recorded through the provided logger.

    Args:
        logger: Logger used to record changes in model selection.

    Returns:
        Name of the model currently selected in the interface.
    """

    if "file_conversion_model" not in st.session_state:
        st.session_state["file_conversion_model"] = "MarkItDown"

    with st.container(border=True):
        header, info = st.columns([3, 1])
        with header:
            st.subheader(body="Model Selection", anchor=False)

        selected_model = st.pills(
            label="Choose your file conversion model",
            options=FILE_CONVERSION_MODELS,
            default=st.session_state["file_conversion_model"],
            selection_mode="single",
        )

    if selected_model != st.session_state["file_conversion_model"]:
        logger.info(f"Model changed to: {selected_model}.")
        st.session_state["file_conversion_model"] = selected_model

    return st.session_state["file_conversion_model"]


def process_uploaded_file(file_uploaded, model: Any) -> str | None:
    """
    Convert an uploaded file to Markdown using the provided model.

    The file is written to a temporary location before being processed by
    the model. The converted text content is extracted from the model’s
    output. When no content is produced, the function returns None.

    Args:
        file_uploaded: Uploaded file retrieved from the interface.
        model: Conversion model used to generate Markdown output.

    Returns:
        Markdown content extracted from the converted file or None when no
            content is available.
    """

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(file_uploaded.name).suffix
    ) as tmp_file:
        tmp_file.write(file_uploaded.getvalue())
        tmp_path = tmp_file.name

    result = model.convert(tmp_path)
    return result.text_content if result.text_content else None


def display_file_uploader_section(model: Any) -> None:
    """
    Render the file uploader section and display conversion results.

    A container is shown with a file uploader widget. When the user
    provides a file, it is processed through the conversion model and the
    resulting text is displayed in a text area.

    Args:
        model: Conversion model used to process uploaded files.

    Returns:
        None
    """

    with st.container(border=True):
        file_uploaded = st.file_uploader(
            "Upload file to convert to Markdown",
        )

        if file_uploaded is not None:
            converted_text = process_uploaded_file(file_uploaded, model)

            if converted_text:
                st.text_area(
                    label="Conversion result",
                    value=converted_text,
                    height=400,
                )


def main() -> None:
    """
    Run the file conversion interface.

    The function initializes logging, loads the selected conversion model,
    and displays the uploader section when a valid model is available.

    Returns:
        None
    """

    logger = create_logger(
        logger_file_name="./logs/", logger_name="transcriptions_logs.log"
    )

    # Model selection
    selected_model_name = get_selected_model(logger=logger)
    model = load_conversion_model(model_name=selected_model_name)

    # Display file uploader and handle conversion
    if model is not None:
        display_file_uploader_section(model=model)


if __name__ == "__main__":
    main()
