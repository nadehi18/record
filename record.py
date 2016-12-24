#!/usr/bin/env python

import pyaudio
import wave
import multiprocessing
from tkinter import *
from time import sleep
import sys
import datetime
import os
import argparse

class App():

    def __init__(self, master, queue, save_file):

        
        frame = Frame(master)

        self.text = StringVar() 
        self.text2 = "Output file: " + save_file
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

    def __exit__(self):
        self.record_queue.put(True)



class Record():

    def __init__(self, queue, output_file, time):

        self.output_file = output_file
        self.time = time
        record = self.record(queue)

    def record(self, queue):

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 48000
        RECORD_SECONDS = self.time
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
        exit()
        
def read_args():

    parser = argparse.ArgumentParser()

    ostype = sys.platform
    if "win32" in ostype:
        filedivider = "\\"
    else:
        filedivider = "/"

    current_dir = os.getcwd()

    gui = True
    filename = None
    save_directory = current_dir 
    seconds = 60

    parser.add_argument("FILENAME", help="The name of the file")
    parser.add_argument("-n", "--nogui", help="Runs the program without opening the GUI", action="store_true")
    parser.add_argument("-u", "--usedate", help="Adds the date to the filename", action="store_true")
    parser.add_argument("-d", "--directory", help="Directory to save the file in")
    parser.add_argument("-m", "--minutes", help="Length of time to record in minutes", type=int)
    parser.add_argument("-s", "--seconds", help="Length of time to record in seconds", type=int)

    args = parser.parse_args()

    filename = args.FILENAME
    if args.nogui:
        gui = False
    if args.usedate:
        filename += str(datetime.datetime.now()).split()[0]
    if args.directory:
        save_directory = args.directory
    if args.minutes:
        seconds = args.minutes * 60
    if args.seconds:
        seconds = args.seconds
   
    if not "." in filename:
        filename += ".wav"
    else:
        split_name = filename.split(".")
        if not split_name[-1] == "wav":
           
            if filename[-1] == ".":
                filename += "wav"
            else:
                filename += ".wav"

    if save_directory[-1] != filedivider:
        save_directory += filedivider

    save_file = save_directory + filename
    
    if os.path.isfile(save_file):
        print("Error: file exists.")
        exit()


    return(gui, save_file, seconds)

if __name__ == '__main__':
  
    args = read_args()
    gui = args[0]
    save_file = args[1]
    time = args[2]

    #Start the record subprocess
    multiprocessing.freeze_support()
    record_queue = multiprocessing.Queue()
    record_process = multiprocessing.Process(target = Record, args=(record_queue, save_file, time,))
    record_process.start()

    if gui == True:

        #Start the main GUI
        root = Tk()
        app = App(root, record_queue, save_file)
        root.mainloop()
