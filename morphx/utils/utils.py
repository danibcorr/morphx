# Standard libraries
import io

# 3pps
import noisereduce as nr
import numpy as np
import streamlit as st
from scipy.io import wavfile
from streamlit.runtime.uploaded_file_manager import UploadedFile


def reduce_noise_audio(audio_value: UploadedFile | None) -> io.BytesIO | None:
	if audio_value is None:
		return None

	bytes_data = audio_value.read()
	buffer = io.BytesIO(bytes_data)

	rate, data = wavfile.read(buffer)

	reduced_noise = nr.reduce_noise(
		y=data, sr=rate, use_torch=True, device=st.session_state.device
	)
	output_buffer = io.BytesIO()
	wavfile.write(output_buffer, rate, reduced_noise.astype(np.int16))
	output_buffer.seek(0)

	return output_buffer
