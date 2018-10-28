import os
import copy
from multiprocessing import Process, Array, Value
import ctypes
import numpy as np
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from kivy.properties import StringProperty

import subprocess

def play():
    l_volumes, r_volumes = np.array([1, 0, 0, 0, 0]), np.array([0, 0, 0, 1, 0])
    shared_music_l_volumes, shared_music_r_volumes = Array("f", l_volumes), Array("f", r_volumes)

    music_process = Process(target=play_music, args=[shared_music_l_volumes, shared_music_r_volumes])
    speaker_process = Process(target=assign_speaker, args=[shared_music_l_volumes, shared_music_r_volumes])
    music_process.start()
    speaker_process.start()
    print(speaker_process.is_alive())
    print("p")
    return "P"

def pick():
    print('pick a file')
    fTyp = [('音声ファイル', '*.wav')]
    iDir = '/home/Documents'
    filename.set(tkFileDialog.askopenfilename(filetypes = fTyp, initialdir = iDir))
    print(filename.get())

class TestApp(App):
    def __init__(self, **kwargs):
        super(TestApp, self).__init__(**kwargs)
        self.title = 'greeting'

    def buttonClicked(self, instance):
        args = ["python", "./src/process.py", self.text]
        subprocess.call(args)
        return "ddd"

    def on_enter(self, ti):
        self.text = ti.text

    def build(self):
        self.text = './src/audio/wav/didnt-know.wav'
        boxLayout = BoxLayout(spacing=10,orientation='vertical')
        ti = TextInput(text=self.text, multiline=False)
        ti.bind(on_text_validate=self.on_enter)
        boxLayout.add_widget(ti)
        button = Button(text='Play')
        button.bind(on_press=self.buttonClicked)
        boxLayout.add_widget(button)
        return boxLayout

def app():
    TestApp().run()

if __name__ == '__main__':
    app()