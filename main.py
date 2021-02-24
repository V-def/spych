"""example of Spych"""
from spych import Spych


spych = Spych(video_file='videos/It’s pronounced GIF.-N1AL2EMvVy0.mp4',
              subtitle_file='videos/It’s pronounced GIF.-N1AL2EMvVy0.en.vtt')
spych.subtitles.read()
spych.subtitles.speech(out_path=f'videos/{spych.directory}/subtitles', mode='pyttsx3')
spych.process()
