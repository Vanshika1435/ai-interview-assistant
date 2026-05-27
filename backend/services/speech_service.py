from faster_whisper import WhisperModel
import tempfile
import os

model = None

def get_model():
    global model
    if model is None:
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
    return model


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    try:
        m = get_model()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        segments, _ = m.transcribe(tmp_path, language="en")
        text = " ".join([seg.text for seg in segments]).strip()
        os.unlink(tmp_path)
        return text

    except Exception as e:
        return f"Transcription error: {str(e)}"