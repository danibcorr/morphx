# Standard libraries
import io
import os
import tempfile
from typing import Final

# 3pps
import streamlit as st
import whisper
from st_copy import copy_button

# Own modules
from morphx.utils import reduce_noise_audio

# Globals
WHISPER_OPTIONS: Final[list[str]] = [
	"tiny",
	"base",
	"small",
	"medium",
	"large",
	"turbo",
]

# Page configuration
st.set_page_config(page_title="Audio Transcription", layout="centered")
st.title("Audio Transcription", anchor=False)


@st.cache_resource(show_spinner=True)
def load_whisper_model(model_name: str) -> whisper.Whisper:
	"""
	Load and cache Whisper model.

	Args:
		model_name: Name of the model selected.

	Returns:
		Whisper model.
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
		| Turbo | ~809 MB | Fast | Excellent | Best balance |""")


def get_selected_model() -> str:
	"""
	Get the selected Whisper model from UI.
	"""

	if "selected_model" not in st.session_state:
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

		# Model selection
		selected_model = st.pills(
			label="Choose your Whisper model",
			options=WHISPER_OPTIONS,
			default=st.session_state["selected_model"],
			selection_mode="single",
		)

	# Update state
	if selected_model != st.session_state["selected_model"]:
		st.session_state["selected_model"] = selected_model

	return st.session_state["selected_model"]


def transcribe_audio(audio_data: io.BytesIO, model: whisper.Whisper) -> str | None:
	"""
	Transcribe audio data using the provided model.
	"""

	# Create temporary file with context manager for automatic cleanup
	with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
		tmp_file.write(audio_data.getvalue())
		tmp_file_path = tmp_file.name

	try:
		# Load audio and transcribe
		audio_array = whisper.load_audio(tmp_file_path)
		result = model.transcribe(audio_array, fp16=False)
		return result["text"]
	except Exception as e:
		st.error(f"Transcription failed: {str(e)}")
		return None
	finally:
		# Clean up temporary file
		if os.path.exists(tmp_file_path):
			os.unlink(tmp_file_path)


def microphone_transcription_tab(model: whisper.Whisper) -> None:
	# Audio input interface
	audio_value = st.audio_input(label="Record a voice message")

	audio_value_cleaned = reduce_noise_audio(audio_value)

	if audio_value_cleaned and st.button(
		"Transcribe", type="primary", key="microphone_transcription"
	):
		with st.spinner("Transcribing audio..."):
			transcription = transcribe_audio(audio_value_cleaned, model)

		if transcription:
			# Text are to show the transcription
			st.text_area(
				label="Transcription result",
				value=transcription,
				height="content",
			)

			col1, col2 = st.columns(2)

			with col1:
				# Add download button for transcription
				st.download_button(
					label="Download Transcription",
					data=transcription,
					file_name="transcription.txt",
					mime="text/plain",
					icon=":material/download:",
				)
			with col2:
				copy_button(transcription)


def file_transcription_tab(model: whisper.Whisper) -> None:
	# Audio input interface
	audio_value = st.file_uploader(
		"Upload audio file",
		accept_multiple_files=False,
	)

	audio_value_cleaned = reduce_noise_audio(audio_value)

	if audio_value_cleaned and st.button(
		"Transcribe", type="primary", key="file_transcription"
	):
		with st.spinner("Transcribing audio..."):
			transcription = transcribe_audio(audio_value_cleaned, model)

		if transcription:
			# Text are to show the transcription
			st.text_area(
				label="Transcription result",
				value=transcription,
				height="content",
			)

			col1, col2 = st.columns(2)

			with col1:
				# Add download button for transcription
				st.download_button(
					label="Download Transcription",
					data=transcription,
					file_name="transcription.txt",
					mime="text/plain",
					icon=":material/download:",
				)
			with col2:
				copy_button(transcription)


def main() -> None:
	"""
	Main transcription tool logic.
	"""

	# Model selection
	selected_model_name = get_selected_model()
	model = load_whisper_model(selected_model_name)

	# Create a container to define the tabs
	with st.container(border=True, horizontal_alignment="distribute"):
		# Create tabs for the transcriptions options
		tab1, tab2, tab3 = st.tabs(
			["Microphone Transcription", "Video Transcription", "File Transcription"]
		)

		# Microphone transcriptions
		with tab1:
			microphone_transcription_tab(model=model)

		# File transcriptions
		with tab3:
			file_transcription_tab(model=model)


if __name__ == "__main__":
	main()
