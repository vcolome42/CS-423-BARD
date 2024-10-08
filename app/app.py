import pygame as pg
import speech_recognition as speech
import sprites

recognizer = speech.Recognizer()
recognizer.dynamic_energy_threshold = False

# pygame setup
pg.init()
pg.font.init()

DEFAULT_FONT = pg.font.SysFont("Arial", 24)
text = "Hello world"
text_surf = DEFAULT_FONT.render(text, False, (255, 255, 255))


screen = pg.display.set_mode((640, 480), pg.RESIZABLE)
clock = pg.time.Clock()
running = True

SPRITE_SHEET = sprites.Spritesheet("tiles.png", (4, 4))

def ask_voice(recognizer):
    out = None
    with speech.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Rec start.")
            audio_text = recognizer.listen(source, timeout=1.0)
            print("Rec end.")
            out = recognizer.recognize_google(audio_text)
            print("Text: " + out)
        except Exception as e:
            print("Sorry, I did not get that:", e)
    return out
def print_voice():
    global text_surf
    print("printing")
    data = ask_voice(recognizer)
    text = "SPEECH: " + data if data is not None else ""
    text_surf = DEFAULT_FONT.render(text, False, (255, 255, 255))
print_voice_debounce = False

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYUP:
            if event.key == pg.K_SPACE:
                text = "LISTENING: "
                text_surf = DEFAULT_FONT.render(text, False, (255, 255, 255))
                print_voice_debounce = True

    screen.fill("black")
    # Render steps
    screen.blit(text_surf, (0, 0))
    screen.blit(SPRITE_SHEET.get_sprite(0), (0, 0))

    # flip buffer to display
    pg.display.flip()

    if print_voice_debounce:
        print_voice()
        print_voice_debounce = False

    clock.tick(60)

pg.quit()