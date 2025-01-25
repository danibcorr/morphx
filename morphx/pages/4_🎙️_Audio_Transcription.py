import datetime
import io
import os
import tempfile

import streamlit as st
import whisper
import numpy as np
import yt_dlp
from audiorecorder import audiorecorder


# Set the page configuration for Streamlit
st.set_page_config(page_title="Audio Transcription", page_icon="🎙️", layout="wide")

# Set the title of the page
st.title("🎙️ Audio Transcription")

# Add a logo to the sidebar
st.sidebar.image("./images/logo.png")


def download_youtube_video(temp_dir: str) -> str:
    """
    Download a YouTube video as an audio file to a temporary directory using yt-dlp.

    Args:
        temp_dir (str): The temporary directory to save the audio file.

    Returns:
        str: The path to the downloaded audio file.
    """

    url = st.text_input(
        "Enter the URL of the YouTube video to transcribe:",
        "https://www.youtube.com/watch?v=YbADVar8tjY",
    )

    if st.button("Download video"):

        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
            "progress_hooks": [lambda d: update_progress(d, progress_bar, status_text)],
        }

        try:

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                info_dict = ydl.extract_info(url, download=True)
                audio_file_path = ydl.prepare_filename(info_dict).replace(
                    ".webm", ".mp3"
                )

            # Remove progress bar when done
            progress_bar.empty()
            status_text.success("Download completed")

            return audio_file_path

        except Exception as e:

            st.error(f"Error downloading video: {str(e)}")

            return ""


def update_progress(d, progress_bar, status_text):
    """
    Update the progress bar based on the download status.

    Args:
        d (dict): Dictionary containing download information.
        progress_bar: The Streamlit progress bar to update.
        status_text: The Streamlit text element to update with the current status.
    """

    if d["status"] == "downloading":

        downloaded_bytes = d.get("downloaded_bytes", 0)
        total_bytes = d.get("total_bytes", 0)

        if total_bytes > 0:

            progress_percentage = downloaded_bytes / total_bytes
            progress_bar.progress(progress_percentage)
            status_text.text(f"Downloading: {progress_percentage:.0%}")

    elif d["status"] == "finished":

        progress_bar.progress(1.0)
        status_text.text("Download finished.")


def load_whisper_model(model_option: str) -> whisper.Whisper:
    """
    Load the Whisper model.

    Args:
        model_option (str): The name of the Whisper model to load.

    Returns:
        whisper.Whisper: The loaded Whisper model.
    """

    return whisper.load_model(model_option, in_memory=True)


def record_audio() -> audiorecorder:
    """
    Record audio using the audiorecorder.

    Returns:
        audiorecorder: The recorded audio.
    """

    return audiorecorder("Click to record", "Click to stop recording")


def transcribe_file(model: whisper.Whisper, file: str) -> str:
    """
    Transcribe an audio file using the Whisper model.

    Args:
        model (whisper.Whisper): The Whisper model to use for transcription.
        file (str): The path to the audio file.

    Returns:
        str: The transcribed text, or None if an error occurred.
    """

    try:

        with st.spinner("Transcribing audio..."):

            result = model.transcribe(file, fp16=False)

        transcription_text = result["text"]
        st.subheader("Transcription")
        st.text_area(
            "Transcription", transcription_text, height=300, label_visibility="hidden"
        )

        return transcription_text

    except Exception as e:

        st.error(f"Error transcribing audio: {str(e)}")

        return None


def save_markdown(text: str, filename: str) -> None:
    """
    Save the transcribed text as a markdown file.

    Args:
        text (str): The text to save.
        filename (str): The name of the file to save.
    """

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    try:

        with open(filename, "w", encoding="utf-8") as f:

            f.write(text)

        st.success(f"Transcription saved as markdown to {filename}")
        st.session_state.transcription_text = None

    except IOError as e:

        st.error(f"IOError: {str(e)}. Please check the file path and permissions.")

    except Exception as e:

        st.error(f"Unexpected error: {str(e)}")


@st.cache_resource
def get_model(option: str) -> whisper.Whisper:
    """
    Get the Whisper model, using caching to avoid reloading.

    Args:
        option (str): The name of the Whisper model to load.

    Returns:
        whisper.Whisper: The loaded Whisper model.
    """

    return load_whisper_model(option)


def main() -> None:

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("File configuration")

        save_path = st.text_input(
            "Enter the path to save the markdown file:",
            value=f"./transcriptions/transcription_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        )

        # Transcription type selection
        transcription_type = st.selectbox(
            "Select transcription type:", ("File", "YouTube", "Microphone")
        )

    with col2:

        st.subheader("Model configuration")

        # Model selection
        st.info(
            """
            + tiny: 39 M Parameters, ~1 GB Required VRAM, ~32x Relative speed
            + base: 74 M Parameters, ~1 GB Required VRAM, ~16x Relative speed
            + small: 244 M Parameters, ~2 GB Required VRAM, ~6x Relative speed
            + medium: 769 M Parameters, ~5 GB Required VRAM, ~2x Relative speed
            + large: 1550 M Parameters, ~10 GB Required VRAM, ~1x Relative speed
            """
        )

        model_option = st.selectbox(
            "Select Whisper model:",
            ("tiny", "base", "small", "medium", "large"),
            index=2,
        )

        model = get_model(model_option)

    with col1:

        if transcription_type == "File":

            filepath = st.text_input("Enter audio file path:")

            if filepath and st.button("Transcribe"):

                transcription_text = transcribe_file(model, filepath)

                if transcription_text:

                    st.session_state.transcription_text = transcription_text

        elif transcription_type == "YouTube":

            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:

                # Download the video only if it's not already downloaded
                if (
                    "audio_path" not in st.session_state
                    or not st.session_state.audio_path
                    or not os.path.exists(st.session_state.audio_path)
                ):

                    st.session_state.audio_path = download_youtube_video(temp_dir)

                # Ensure the audio file path is valid before attempting transcription
                if st.session_state.audio_path and os.path.exists(
                    st.session_state.audio_path
                ):

                    if "transcription_text" not in st.session_state:

                        st.session_state.transcription_text = transcribe_file(
                            model, st.session_state.audio_path
                        )

        else:

            audio = record_audio()

            if len(audio) > 0:

                st.audio(audio.export().read())

                # Convert audio to the format expected by Whisper
                audio_buffer = io.BytesIO()
                audio.export(audio_buffer, format="wav", parameters=["-ar", str(16000)])
                file = (
                    np.frombuffer(audio_buffer.getvalue()[44:], dtype=np.int16).astype(
                        np.float32
                    )
                    / 32768.0
                )

                if st.button("Transcribe"):

                    transcription_text = transcribe_file(model, file)

                    if transcription_text:

                        st.session_state.transcription_text = transcription_text

    if (
        "transcription_text" in st.session_state
        and st.session_state.transcription_text is not None
    ):

        if st.button("Save as Markdown"):

            save_markdown(st.session_state.transcription_text, save_path)


if __name__ == "__main__":

    main()
