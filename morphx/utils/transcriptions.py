# Standard libraries
import io
import logging
import os
import tempfile

# 3pps
import noisereduce as nr
import numpy as np
import streamlit as st
import whisper
from pydub import AudioSegment
from scipy.io import wavfile
from streamlit.runtime.uploaded_file_manager import UploadedFile


def transcribe_audio(
    audio_data: io.BytesIO, model: whisper.Whisper, logger: logging.Logger
) -> str | None:
    """
    Transcribe audio stored in memory using the provided model.

    The audio buffer is written to a temporary file so it can be parsed
    by the transcription backend. After loading the audio into an array,
    the model generates a text transcription. Any issues encountered
    during processing are logged and surfaced to the interface.

    Args:
        audio_data: Audio content stored in memory.
        model: Whisper model used to generate the transcription.
        logger: Logger used to record transcription activity.

    Returns:
        Transcribed text, or None when transcription cannot be
            completed.
    """

    logger.info("Create temporary file for audio transcription.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_data.getvalue())
        tmp_file_path = tmp_file.name

    try:
        logger.info("Loading audio and transcribing.")
        audio_array = whisper.load_audio(tmp_file_path)
        result = model.transcribe(audio_array, fp16=False)
        return result["text"]
    except Exception as e:
        error_message: str = f"Transcription failed: {str(e)}."
        logger.error(error_message)
        st.error(error_message)
        return None
    finally:
        logger.info("Clean up temporary file.")
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


def reduce_noise_audio(
    audio_value: UploadedFile | io.BytesIO | None, logger: logging.Logger
) -> io.BytesIO | None:
    """
    Apply noise reduction to audio from an upload or in-memory buffer.

    The input is normalized to an in-memory WAV buffer, which is then
    processed using a noise-reduction algorithm. A cleaned audio buffer
    is returned for further processing. When no input is provided or the
    format is unsupported, the function records the issue and returns no
    output.

    Args:
        audio_value: Audio obtained from the user interface or an
            in-memory buffer.
        logger: Logger used to record processing activity.

    Returns:
        Cleaned audio buffer, or None when processing cannot be
            completed.
    """

    if audio_value is None:
        return None

    match audio_value:
        case UploadedFile():
            bytes_data = audio_value.read()
            buffer = io.BytesIO(bytes_data)
        case io.BytesIO():
            buffer = audio_value
            buffer.seek(0)
        case _:
            logger.error(
                "Unknown 'audio_value' type, needs to be UploadedFile or io.BytesIO"
            )
            return None

    try:
        rate, data = wavfile.read(buffer)

        device = st.session_state.get("device", "cpu")
        reduced_noise = (
            nr.reduce_noise(y=data, sr=rate, use_torch=True, device=device)
            if device == "cuda"
            else nr.reduce_noise(y=data, sr=rate, device=device)
        )

        output_buffer = io.BytesIO()
        wavfile.write(output_buffer, rate, reduced_noise.astype(np.int16))
        output_buffer.seek(0)

        return output_buffer
    except Exception as e:
        error_message = f"Noise reduction failed: {str(e)}"
        logger.error(error_message)
        st.error(error_message)
        return None


def convert_audio_to_wav(
    audio_file: UploadedFile, logger: logging.Logger
) -> io.BytesIO | None:
    """
    Convert an uploaded audio file to a WAV buffer suitable for
    transcription.

    The uploaded file is decoded according to its format and then
    re-encoded into a standardized WAV file with settings compatible
    with the transcription model. The result is returned in memory
    without writing to disk.

    Args:
        audio_file: Audio file provided through the user interface.
        logger: Logger used to record convertion activity.

    Returns:
        In-memory WAV audio data prepared for transcription.
    """

    try:
        audio_bytes = audio_file.read()
        file_extension = audio_file.name.split(".")[-1].lower()
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=file_extension)

        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav", parameters=["-ar", "16000", "-ac", "1"])
        wav_buffer.seek(0)

        return wav_buffer
    except Exception as e:
        error_message = f"Audio conversion failed: {str(e)}"
        logger.error(error_message)
        st.error(error_message)
        return None
