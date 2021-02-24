"""subtitles"""


class Subtitles:
    """subtitles class"""

    def __init__(self, file, language='en'):
        self.list = []
        self.file = file
        self.language = language

    def read(self):
        """read the subtitle file and convert it into table"""
        if not self.list:
            if self.file:
                with open(str(self.file), 'r', encoding='utf-8-sig') as f:
                    if self.file.extension == '.vtt':
                        for n, sequence in enumerate(f.read().split('\n\n')[1:]):
                            temp = sequence.split('\n')
                            time = temp[0].split(' --> ')
                            text = ' '.join(temp[1:])
                            if time != '' and text != '':
                                subtitle = {"n": n, "time": time, "text": text}
                                self.list.append(subtitle)
                    elif self.file.extension == '.srt':
                        for sequence in f.read().split('\n\n'):
                            temp = sequence.split('\n')
                            n = int(temp[0])
                            time = temp[1].split(' --> ')
                            text = '\n'.join(temp[2:])
                            if time != '' and text != '':
                                subtitle = {"n": n, "time": time, "text": text}
                                self.list.append(subtitle)
                    else:
                        raise Exception(f'unknown subtitle format : "{self.file.extension}"')
            else:
                raise FileNotFoundError(f'cannot find {self.file}')

    def speech(self, out_path='', mode='pyttsx3'):
        """convert table into speech in mp3"""
        if mode == 'pyttsx3':
            self.speech_pyttsx3(out_path=out_path)
        elif mode == 'gtts':
            self.speech_gtts(out_path=out_path)

    def speech_pyttsx3(self, out_path=''):
        """convert table into speech in mp3 using pyttsx3 module
        conversion is made locally"""
        import pyttsx3

        engine = pyttsx3.init()
        # change property about engine here

        for sequence in self.list:
            # change property about engine locally here
            engine.save_to_file(sequence["text"], f'{out_path}/seq-{sequence["n"]}.mp3')
        engine.runAndWait()

    def speech_gtts(self, out_path=''):
        """convert table into speech in mp3 using gtts module
        warning : uses internet to request google translate"""
        from gtts import gTTS
        from gtts.tokenizer import pre_processors

        for sequence in self.list:
            sequence["text"] = pre_processors.word_sub(sequence["text"])
            speech = gTTS(text=sequence["text"], lang=self.language, slow=False)
            speech.save(f'{out_path}/seq-{sequence["n"]}.mp3')
