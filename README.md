# CS-423-BARD

BARD's goal is to transform a classic game (Rogue) into a natural user experience using a voice-controlled user interface. By developing, implementing and iterating on the human interaction cycle, we aim to allow the user to control the game seamlessly as if they were in the game itself, maximizing immersion and gameplay enjoyment.

![Screenshot of latest Rogue version and window.](screenshot.png?raw=true)

# Prerequisites
- Python 3.12 installed on your machine.
- pip (Check using `pip --version`)
- venv (Check using `python -m venv --help`)

# Setup
1. Verify and install prerequisites.

2. Clone `git clone https://github.com/vcolome42/CS-423-BARD.git`

3. Move into the project directory `cd CS-423-BARD`

4. Create virtual environment using `python -m venv venv`

5. Ensure that the virtual environment has started
On Windows
`venv\Scripts\activate`
On macOS/Linux
`source venv/bin/activate`

6. Install requirements using `pip install -r requirements.txt`

7. Move into the folder using `cd app`

8. Run the program using `python app.py`
WARNING: `python app/app.py` will not work.
PyGame requires the working directory to be set to app/ in order to properly load resources

# Troubleshooting

## Voice recognition is slow
The Whisper model has to download and set up the first time you use the program's voice recognition.
After you download it once, it will not need to download again, but does need to initialize still
after the app has restarted.

## Microphone not working
A good sanity check for if your microphone is working properly is to check if the dynamic threshold
calibration value is a normal value.
After the app starts, it will calibrate the energy_threshold. A nominal value ranges from 180-2000.
If the threshold is set too high (~3000-4000), that means your mic is too loud, and you may need to
adjust it in the Sound Control Panel.
If the threshold is really quiet ~0, it's possible that it your mic may be completely silent.
This may not be true if you're using noise removal software or high dynamic range microphones.

# Assets Used
Info Font: https://managore.itch.io/m3x6
Daniel Linssen

# References
Zhang, A. (2017). Speech Recognition (Version 3.11) [Software]. Available from https://github.com/Uberi/speech_recognition#readme.
