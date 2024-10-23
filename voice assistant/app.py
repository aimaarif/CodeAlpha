from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import wikipedia
import pyttsx3

app = Flask(__name__)

# Initialize pyttsx3 engine for text-to-speech
engine = pyttsx3.init()

@app.route('/')
def index():
    return render_template('index.html')

from pydub import AudioSegment
import speech_recognition as sr
import os

def convert_to_wav(audio_file):
    # Convert the uploaded audio to WAV using pydub
    audio = AudioSegment.from_file(audio_file)
    wav_file_path = os.path.splitext(audio_file)[0] + ".wav"
    audio.export(wav_file_path, format="wav")
    return wav_file_path


@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    wav_file_path = convert_to_wav(audio_file)
    # Initialize speech recognition
    recognizer = sr.Recognizer()

    try:
        # Recognize speech from the audio file
        with sr.AudioFile(wav_file_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print(f"Recognized Text: {text}")

        # Search Wikipedia using recognized text
        wiki_summary = wikipedia.summary(text, sentences=2)
        print(f"Wikipedia Summary: {wiki_summary}")

        # Convert Wikipedia summary to speech
        engine.say(wiki_summary)
        engine.runAndWait()

        return jsonify({'message': text, 'summary': wiki_summary})

    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand the audio'}), 400
    except sr.RequestError:
        return jsonify({'error': 'Speech Recognition service failed'}), 500
    except wikipedia.DisambiguationError:
        return jsonify({'error': 'Multiple results found. Be more specific'}), 400
    except wikipedia.PageError:
        return jsonify({'error': 'No Wikipedia page found for the query'}), 404

if __name__ == '__main__':
    app.run(debug=True)