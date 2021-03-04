"""example of Spych"""
from spych import Spych


# spych = Spych(directory='Its pronounced GIF')
# spych = Spych(
#    video_file="videos/Its pronounced GIF/Its pronounced GIF.mp4",
#    subtitle_file="videos/Its pronounced GIF/Its pronounced GIF.en.vtt")
# spych = Spych(quarry="Tom Scott GIF")

quarry = input("Enter search terms :")
spych = Spych(quarry=quarry)
spych.speech(depth=3)
spych.process(correct_speed=False)
input("Success")
