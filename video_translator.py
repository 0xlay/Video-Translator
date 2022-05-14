import math
import shutil
import speech_recognition as sr
import pyttsx3
from moviepy.editor import *
from pydub import AudioSegment
from deep_translator import GoogleTranslator


class SplitWavAudio():
    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.audio = AudioSegment.from_wav(self.filename)
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        os.mkdir(folder)

    def __del__(self):
        shutil.rmtree(self.folder)

    def get_duration(self):
        return self.audio.duration_seconds

    def single_split(self, from_min, to_min, split_filename):
        t1 = from_min * 60 * 1000
        t2 = to_min * 60 * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(self.folder + '\\' + split_filename, format='wav')

    def multiple_split(self, min_per_split):
        total_mins = math.ceil(self.get_duration() / 60)
        for i in range(0, total_mins, min_per_split):
            split_fn = str(i) + '_' + self.filename
            self.single_split(i, i + min_per_split, split_fn)
            if i == total_mins - min_per_split:
                print('All splited successfully.')


def audios_to_text(path_to_folder: str, source_file: str, lang: str) -> str:
    r = sr.Recognizer()
    text: str = ""
    quantity_files = len(os.listdir(path_to_folder))
    for i in range(0, quantity_files):
        with sr.AudioFile(path_to_folder + "\\" + str(i) + "_" + source_file) as source:
            audio_data = r.record(source)
            try:
                text += r.recognize_google(audio_data, language=lang)
                print(f"Audio {i} of {quantity_files} converted to text.")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio.")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}.".format(e))
    return text


def translate(text: str, target_lang: str) -> str:
    chunks = len(text)
    chunk = 4999 # max size chunk to translate
    if chunks > chunk:
        translated: str = ''
        sentences = [text[i:i + chunk] for i in range(0, chunks, chunk)]
        for sentence in sentences:
            translated += GoogleTranslator(source='auto', target=target_lang).translate(sentence)
        return translated
    return GoogleTranslator(source='auto', target=target_lang).translate(text)


def main():
    path = input('Enter path to video (with file extension: \'video.mp4\'): ')
    source_lang = input('Source lang video (en-US, es-ES, uk, ru, ...): ')
    target_lang = input('Target lang video (en-US, es-ES, uk, ru, ...): ')

    # Locale codes
    # https://www.science.co.il/language/Locale-codes.php

    # Convert video to audio:

    audio_clip = AudioFileClip(path) # "1. Session 1 - Part 1.m4v"
    audio_clip.write_audiofile("our_audio.wav")

    # split audio to sub-audio

    folder = 'split_wav_files'
    file_name = 'our_audio.wav'
    split_wav = SplitWavAudio(folder, file_name)
    split_wav.multiple_split(min_per_split=1)

    text = audios_to_text(folder, file_name, source_lang)
    with open("original_subtitles.txt", "w", encoding="utf-8") as file:
        file.write(text)

    translated_text = translate(text, target_lang)
    with open("translated_subtitles.txt", "w", encoding="utf-8") as file:
        file.write(translated_text)

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    len_voices = 0
    for voice in voices:
        len_voices += 1
        print('------------------------------------------------------------------------------------------')
        print(f'Name: {voice.name}')
        print(f'ID: {voice.id}')
        print(f'Lang: {voice.languages}')
        print(f'Sex: {voice.gender}')
        print(f'Age: {voice.age}')

    print('------------------------------------------------------------------------------------------')
    voice_index = int(input(f'\nChoose voice (1 - {len_voices}): '))

    engine.setProperty('voice', voices[voice_index - 1].id)
    engine.setProperty('rate', 150) # 150 - default
    engine.setProperty('volume', 0.9)

    engine.save_to_file(translated_text, "translated_audio.mp3")

    engine.runAndWait()


if __name__ == '__main__':
    sys.exit(main())
