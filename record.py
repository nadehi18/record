import pyaudio
import wave
import multiprocessing
from tkinter import *
from time import sleep
import sys
import datetime

class App():

    def __init__(self, master, queue, save_dir):

        
        frame = Frame(master)

        self.output_file = date = str(datetime.datetime.now()).split()[0] 
        self.text = StringVar() 
        self.text2 = "Output file: " + save_dir + self.output_file + '.wav'
        self.record_queue = queue

        self.textbox = Label(master, textvariable=self.text).pack()
        self.textbox2 = Label(master, text=self.text2)
        self.button = Button(master, text="Stop and Save Recording", command=self.finish_record)
        self.button.pack()
        self.button2 = Button(master, text="Ok", command=frame.quit)
        frame.pack()
        
        self.text.set("Status: Recording")

    def finish_record(self):
        self.record_queue.put(True)

        self.text.set("Status: Saving")
        self.textbox2.pack()
        self.button.destroy()

        self.button2.pack()
        self.text.set("Status: Done")

class Record():

    def __init__(self, queue, output_dir, minutes):

        date = str(datetime.datetime.now()).split()[0]
        self.output_file = output_dir + date  + '.wav'
        if minutes > 0:
            self.record_minutes = minutes
        else:
            self.record_minutes = 110
        record = self.record(queue)

    def record(self, queue):

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 48000
        RECORD_SECONDS = self.record_minutes * 60
        WAVE_OUTPUT_FILENAME = self.output_file

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
                    
            #Stop recording if message was sent through queue
            if not queue.empty():
                break

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        


if __name__ == '__main__':

    multiprocessing.freeze_support()

    #Handle arguments (needs to be redone)
    if len(sys.argv) == 3:
        save_dir = sys.argv[1]
        minutes = sys.argv[2]
    elif len(sys.argv) == 2:
        save_dir = sys.argv[1]
        minutes = 0
    else:
        save_dir = ""
        minutes = 0

    #Start the record subprocess
    record_queue = multiprocessing.Queue()
    record_process = multiprocessing.Process(target = Record, args=(record_queue, save_dir, minutes,))
    record_process.start()

    #Start the main GUI
    root = Tk()
    app = App(root, record_queue, save_dir)
    root.mainloop()
