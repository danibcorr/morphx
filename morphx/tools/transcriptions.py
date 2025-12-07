# Standard libraries
import logging

# 3pps
import streamlit as st
import whisper

# Own modules
from morphx.configs import WHISPER_OPTIONS
from morphx.utils import (convert_audio_to_wav, create_logger, reduce_noise_audio,
                          transcribe_audio)

# Page configuration
st.set_page_config(page_title="Audio Transcription", layout="centered")
st.title("Audio Transcription", anchor=False)


@st.cache_resource(show_spinner=True)
def load_whisper_model(model_name: str) -> whisper.Whisper:
    """
    Load a Whisper model and cache the instance for reuse across sessions.

    The model is retrieved using the provided name and kept in memory to
    avoid repeated initialization during the application lifecycle. The
    logger records when the model is being loaded.

    Args:
        model_name: Name of the Whisper model to load.
        logger: Logger used to record model loading events.

    Returns:
        Loaded Whisper model instance.
    """

    return whisper.load_model(model_name, in_memory=True)


@st.dialog("About audio transcription model")
def model_information() -> None:
    st.markdown("""
		The model used for the transcripts is Whisper, and the settings
		offered by the model are as follows:

		| Model | Size | Speed | Accuracy | Best For |
		|-------|------|-------|----------|----------|
		| Tiny | ~39 MB | Fastest | Good | Quick drafts |
		| Base | ~74 MB | Fast | Better | General use |
		| Small | ~244 MB | Medium | Good | Balanced performance |
		| Medium | ~769 MB | Slower | Very Good | High accuracy needs |
		| Large | ~1550 MB | Slowest | Excellent | Professional use |
		| Turbo | ~809 MB | Fast | Excellent | Best balance |
    """)


def get_selected_model(logger: logging.Logger) -> str:
    """
    Retrieve the Whisper model selected in the user interface.

    The selection is persisted in the session state so the chosen model
    remains consistent across interactions. When no model has been chosen
    yet, a default value is applied. A header and informational dialog are
    displayed alongside selectable model options.

    Args:
        logger: Logger used to record model loading events.

    Returns:
        Name of the Whisper model currently selected.
    """

    if "selected_model" not in st.session_state:
        logger.info("By default 'turbo' model is selected for Whisper model.")
        st.session_state["selected_model"] = "turbo"

    with st.container(border=True, horizontal_alignment="distribute"):
        header, info = st.columns([3, 1])

        with header:
            st.subheader(body="Model Selection", anchor=False)
        with info:
            if st.button(
                "Model Info", icon=":material/info:", use_container_width=True
            ):
                model_information()

        selected_model = st.pills(
            label="Choose your Whisper model",
            options=WHISPER_OPTIONS,
            default=st.session_state["selected_model"],
            selection_mode="single",
        )

    if selected_model != st.session_state["selected_model"]:
        logger.info(f"Model changed to: {selected_model}.")
        st.session_state["selected_model"] = selected_model

    return st.session_state["selected_model"]


def audio_processing_pipeline(
    audio_value, model: whisper.Whisper, logger: logging.Logger, button_key: str
) -> None:
    """
    Executes a full audio-to-text workflow, including conversion to WAV,
    noise reduction, transcription, and displaying results in a Streamlit
    interface. The function runs sequentially and performs each stage only
    when the previous one succeeds.

    Args:
        audio_value: Raw uploaded audio data used as the input source.
        model: Model used to produce the transcription output.
        logger: Logger used to record workflow events.
        button_key: Identifier used to register the transcription button.

    Returns:
        None. The function updates the Streamlit interface with output
            elements such as messages, a text area, and a download option.
    """

    if audio_value is None:
        return

    audio_value_wav = convert_audio_to_wav(audio_file=audio_value, logger=logger)

    if audio_value_wav is None:
        st.error("Failed to convert audio file to WAV format.")
        return

    audio_value_cleaned = reduce_noise_audio(audio_value=audio_value_wav, logger=logger)

    if not audio_value_cleaned:
        st.error("Failed to clean audio.")
        return

    # Status to check whether it has been transcribed
    transcribed_key = f"{button_key}_transcribed"

    if transcribed_key not in st.session_state:
        st.session_state[transcribed_key] = False

    # Show download button ONLY if it has not been transcribed
    if not st.session_state[transcribed_key]:
        st.download_button(
            label="Download Cleaned Audio",
            data=audio_value_cleaned,
            file_name="cleaned_audio.wav",
            mime="audio/wav",
            icon=":material/download:",
            use_container_width=True,
            key=f"{button_key}_download_1",
        )

    if st.button("Transcribe", type="primary", key=button_key):
        with st.spinner("Transcribing audio..."):
            transcription = transcribe_audio(
                audio_data=audio_value_cleaned, model=model, logger=logger
            )

        if transcription:
            logger.info("Transcription completed successfully.")

            # Save to status
            st.session_state[transcribed_key] = True
            st.session_state[f"{button_key}_text"] = transcription
            st.session_state[f"{button_key}_audio"] = audio_value_cleaned

            # Force rerun to refresh the UI
            st.rerun()

    if st.session_state[transcribed_key]:
        transcription = st.session_state.get(f"{button_key}_text", "")
        audio_cleaned = st.session_state.get(f"{button_key}_audio", None)

        st.text_area(
            label="Transcription result",
            value=transcription,
            height="content",
        )

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Download Transcription",
                data=transcription,
                file_name="transcription.txt",
                mime="text/plain",
                icon=":material/download:",
                use_container_width=True,
                key=f"{button_key}_download_transcription",
            )

        with col2:
            st.download_button(
                label="Download Cleaned Audio",
                data=audio_cleaned,
                file_name="cleaned_audio.wav",
                mime="audio/wav",
                icon=":material/download:",
                use_container_width=True,
                key=f"{button_key}_download_2",
            )


def microphone_transcription_tab(
    model: whisper.Whisper, logger: logging.Logger
) -> None:
    """
    Render the microphone-based transcription interface.

    Args:
        model: Whisper model used to generate the transcription.
        logger: Logger used to record model loading events.

    Returns:
        None
    """

    audio_value = st.audio_input(
        label="Record a voice message", sample_rate=16000, width="stretch"
    )

    audio_processing_pipeline(
        audio_value=audio_value,
        model=model,
        logger=logger,
        button_key="microphone_transcription",
    )


def file_transcription_tab(model: whisper.Whisper, logger: logging.Logger) -> None:
    """
    Render the file-based transcription interface.

    Args:
        model: Whisper model used to generate the transcription.
        logger: Logger used to record model loading events.

    Returns:
        None
    """

    audio_value = st.file_uploader(
        "Upload audio file",
        accept_multiple_files=False,
    )

    audio_processing_pipeline(
        audio_value=audio_value,
        model=model,
        logger=logger,
        button_key="file_transcription",
    )


def main() -> None:
    """
    Coordinate the complete audio transcription workflow.

    The main function handles model selection, loads the chosen Whisper
    model, and presents the application’s two primary interfaces: one for
    microphone recording and one for audio file uploads. Each interface
    enables audio cleaning and transcription.

    Returns:
        None
    """

    logger = create_logger(
        logger_file_name="./logs/", logger_name="transcriptions_logs.log"
    )

    # Model selection
    selected_model_name = get_selected_model(logger=logger)
    model = load_whisper_model(model_name=selected_model_name)

    # Create a container to define the tabs
    with st.container(border=True, horizontal_alignment="distribute"):
        tab1, tab2 = st.tabs(["Microphone Transcription", "File Transcription"])

        with tab1:
            microphone_transcription_tab(model=model, logger=logger)
        with tab2:
            file_transcription_tab(model=model, logger=logger)


if __name__ == "__main__":
    main()
