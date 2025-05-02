import speech_recognition as sr
import keyboard
import time

recognizer = sr.Recognizer()
mic = sr.Microphone()

print("🎙️ Say 'play play' or 'pause pause' to control media...")

while True:
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("🟢 Listening...")
            audio = recognizer.listen(source, timeout=5)

        command = recognizer.recognize_google(audio).lower()
        print(f"👂 Heard: {command}")

        if "start" in command:
            print("▶️ Play command detected!")
            keyboard.send("play/pause media")

        elif "stop" in command:
            print("⏸️ Pause command detected!")
            keyboard.send("play/pause media")

    except sr.WaitTimeoutError:
        print("⏳ Listening timed out, retrying...")

    except sr.UnknownValueError:
        print("🤷 Didn't catch that, say it again.")

    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(1)
