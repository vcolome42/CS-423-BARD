# Make sure you have done the following before running the code:
# 1) pip install SpeechRecognition
# 2) python -m pip install pyaudio
# 3) pip install setuptools (this is in case you get an error saying "No module named distutils)


import speech_recognition as sr

# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()

# Reading Microphone as source
# listening the speech and store in audio_text variable

print(sr.Microphone.list_microphone_names())
print(sr.Microphone.list_working_microphones())

with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source, duration=1)
    print("Talk")
    audio_text = r.listen(source)
    print("Time over, thanks")
    # recoginze_() method will throw a request
    # error if the API is unreachable,
    # hence using exception handling

    try:
        # using google speech recognition
        print("Text: " + r.recognize_google(audio_text))
    except Exception as e:
        print("Sorry, I did not get that:", e) # Print exception
