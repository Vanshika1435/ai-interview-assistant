from faster_whisper import WhisperModel
import tempfile
import os

model = None

def get_model():
    global model
    if model is None:
        model = WhisperModel("tiny", device="cpu", compute_type="int8", cpu_threads=1, num_workers=1)
    return model


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    try:
        m = get_model()
        _, ext = os.path.splitext(filename or "")
        suffix = ext if ext else ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        segments, _ = m.transcribe(tmp_path, language="en")
        text = " ".join([seg.text for seg in segments]).strip()
        os.unlink(tmp_path)
        return text or ""

    except Exception as e:
        return f"Transcription error: {str(e)}"