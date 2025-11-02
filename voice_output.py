import pyttsx3
import threading

engine = pyttsx3.init()
engine.setProperty('rate', 165)
voices = engine.getProperty('voices')

# Optional: Use female voice if available
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)

# Internal control variables
is_speaking = False
speech_thread = None
stop_flag = False


def _speak_background(text):
    """Speak text safely in background thread."""
    global is_speaking, stop_flag
    is_speaking = True
    stop_flag = False
    try:
        for sentence in text.split(". "):
            if stop_flag:
                break
            engine.say(sentence)
            engine.runAndWait()
    except Exception as e:
        print(f"Error in speaking: {e}")
    finally:
        is_speaking = False
        stop_flag = False


def speak_text(text):
    """Start speaking text in background thread."""
    global speech_thread
    stop_speaking()  # Stop any ongoing speech
    speech_thread = threading.Thread(target=_speak_background, args=(text,), daemon=True)
    speech_thread.start()


def stop_speaking():
    """Stop speaking immediately."""
    global is_speaking, stop_flag
    if is_speaking:
        stop_flag = True
        engine.stop()
        is_speaking = False
