import pygame
import os

os.startfile("country.mid")
pygame.mixer.pre_init(44100,-16,2,1024)
pygame.init()
pygame.mixer.music.set_volume(0.8)

#pygame.mixer.music.load("country.mid")
#pygame.mixer.music.play()
#while pygame.mixer.music.get_busy():
#    pygame.time.wait(1000)

def play_music(midi_filename):
    clock = pygame.time.Clock()
    with open(midi_filename,"rb") as musicfile:
        pygame.mixer.music.load(musicfile)
        print("Loaded")
    pygame.mixer.music.play(loops=-1)
    print("Playing")
    while pygame.mixer.music.get_busy():
        print("pygame mixer works")
        clock.tick(30)

midi_filename = "strangers.ogg"

play_music(midi_filename)