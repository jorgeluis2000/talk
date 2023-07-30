import speech_recognition as sr
import tkinter.filedialog as fd
import tkinter as tk
from tkinter import ttk
import moviepy.editor as mvp
import os
import pydub
from pydub import AudioSegment
from pydub.silence import split_on_silence
import datetime
from tkinter import messagebox as mb


def transformAudio(fileP, typ="mp3"):
    sound = None
    if not os.path.exists("audio/audios"):
        os.makedirs("audio/audios")

    newAudio = "audio/audios/new_file.wav"

    if typ == "mp3":
        sound = AudioSegment.from_mp3(fileP)
        sound.export(newAudio, format="wav")
    elif typ == "flv":
        sound = AudioSegment.from_flv(fileP)
        sound.export(newAudio, format="wav")
    elif typ == "mp4":
        video = mvp.VideoFileClip(fileP)
        video.audio.write_audiofile("audio/audios/new_file.mp3")
        sound = AudioSegment.from_mp3("audio/audios/new_file.mp3")
        sound.export(newAudio, format="wav")
    else:
        sound = AudioSegment.from_wav(fileP)
        sound.export(newAudio, format="wav")

    return newAudio


def conversionSpeakOfAudioToText(lang='es-Es'):
    r = sr.Recognizer()
    fh = open("recognized.txt", "w+")
    dialog = ""
    with sr.Microphone() as source:
        print("Say something...\n")
        #r.adjust_for_ambient_noise(source)
        audio_listened = r.listen(source)
        try:
            rec = r.recognize_google(audio_listened, language=lang)
            dialog += str(rec) + ". "
            fh.write(rec + ". ")
            print("You said: {0}".format(rec))
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.Recognizer as e:
            print("Could not request results. check your internet connection")
    fh.close()
    return dialog
    # readAndWrite()


def silence_based_conversion(path="record.wav", typ="wav", lang='es-Es', min_len_silence=2000, silence_frequently=-100):
    song = AudioSegment.from_wav(transformAudio(path, typ))
    fh = open("recognized.txt", "w+")
    typ = "wav"
    print("Time: {0}".format(str(len(song))))
    x = datetime.datetime.now()
    print("{hour}:{min}:{sec}".format(hour=x.strftime("%H"), min=x.strftime("%M"), sec=x.strftime("%S")))
    startX = str("{hour}:{min}:{sec}".format(hour=x.strftime("%H"), min=x.strftime("%M"), sec=x.strftime("%S")))
    chunks = split_on_silence(song, min_silence_len=min_len_silence, silence_thresh=silence_frequently, seek_step=1)
    try:
        os.mkdir("audio/audio_chunks")
    except FileExistsError:
        print("didn't find that file")
    i = 0
    print("Mount chunks: {count}".format(count=len(chunks)))
    for chunk in chunks:
        chunk_silent = AudioSegment.silent(duration=10)
        audio_chunk = chunk_silent + chunk + chunk_silent
        print("saving_chunk{iterator}.{type}".format(iterator=i, type=typ))
        filename = 'chunk' + str(i) + '.' + typ
        file = "audio/audio_chunks/" + filename
        audio_chunk.export(file, bitrate='192k', format=typ)
        print("Processing chunk " + str(i))
        r = sr.Recognizer()
        with sr.AudioFile(file) as source:
            r.adjust_for_ambient_noise(source)
            audio_listened = r.listen(source)
            try:
                rec = r.recognize_google(audio_listened, language=lang)
                fh.write(rec + ". ")
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.Recognizer as e:
                print("Could not request results. check your internet connection")
        i += 1
    x = datetime.datetime.now()
    print("End time - {hour}:{min}:{sec}".format(hour=x.strftime("%H"), min=x.strftime("%M"), sec=x.strftime("%S")))
    endX = str(
        "End time - {hour}:{min}:{sec}".format(hour=x.strftime("%H"), min=x.strftime("%M"), sec=x.strftime("%S")))
    fh.close()
    return readAndWrite("recognized.txt"), startX, endX


def readAndWrite(fileName="recognized.txt"):
    fo = open(fileName, 'r+')
    print('The container is: \n')
    strText = ""
    for line in fo:
        strText += line
    print(strText)
    return strText


def chooseFile():
    pickedFileTypes = (('wav files', '*.wav'), ('mp3 files', '*.mp3'), ('wav files', '*.wav'), ('mp4 files', '*.mp4'))
    file = fd.askopenfilename(initialdir=os.getcwd(), title="Please select a file:", filetypes=pickedFileTypes)
    typ = str(file).split(".")
    typ = typ[len(typ) - 1]
    return file, typ


class Controller:

    def __init__(self):
        super(Controller, self).__init__()
        self.__root = FrameViewMain()
        self.__root.title('Speak Recognize')
        # self.__root.geometry('1000x800')
        self.__root.resizable(width=True, height=False)
        self.__root.config(bg="snow2")
        self.__root.protocol("WM_DELETE_WINDOW", self.beforeCloseWindow)
        self.__file = ""
        self.__typ = ""
        self.actionClick()
        self.__root.mainloop()

    def actionClick(self):
        self.__root.frameContainer.loadFileBT['command'] = self.loadFile
        self.__root.frameContainer.speakAndWriteBT['command'] = self.speakSomething
        self.__root.frameContainer.writeFileLoad['command'] = self.writeSomething

    def beforeCloseWindow(self):
        if mb.askyesno("Closing window", "You're sure to close this Software?"):
            self.__root.destroy()
        else:
            mb.showinfo('Canceled', 'Canceled the action')

    def loadFile(self):
        self.__file, self.__typ = chooseFile()
        self.__root.lbDataLoadR.config(text=self.__file, fg="red")

    def writeSomething(self):
        tipo = str(self.__root.combBox.get())
        if self.__file != "":
            if tipo != "":
                if tipo == "Spanish":
                    tipo = "es-Es"
                else:
                    tipo = "en-En"
                conversation, timeStart, timeEnd = silence_based_conversion(self.__file, lang=tipo,
                                                                            typ=self.__typ, min_len_silence=int(self.__root.spLongSilence.get()), silence_frequently=int(self.__root.spDownFrequently.get()))
                self.__root.lbTimeStartR.config(text=timeStart, fg="red")
                self.__root.frameContainer.txtTranscription.delete("1.0", tk.END)
                self.__root.frameContainer.txtTranscription.insert("1.0", conversation)
                self.__root.lbTimeEndR.config(text=timeEnd, fg="red")
            else:
                mb.showwarning("Select a language", "Please, you must select a language to into")
        else:
            mb.showwarning("Select a File", "Please, you must select a File")

    def speakSomething(self):
        tipo = str(self.__root.combBox.get())
        if tipo != "":
            if tipo == "Spanish":
                tipo = "es-Es"
            else:
                tipo = "en-En"
            conversation = conversionSpeakOfAudioToText(lang=tipo)
            self.__root.frameContainer.txtTranscription.delete("1.0", tk.END)
            self.__root.frameContainer.txtTranscription.insert("1.0", conversation)
        else:
            mb.showwarning("Select a language", "Please, you must select a language to into")


class FrameViewMain(tk.Tk):

    def __init__(self):
        super(FrameViewMain, self).__init__()

        # Creating objects
        self.scrollingRight = tk.Scrollbar(self)
        self.frameResource = tk.Frame(self, bg="snow2")
        self.__frameContainerTop = tk.Frame(self.frameResource, bg='snow2')
        self.__frameContainerBo = tk.Frame(self.frameResource, bg='snow2')
        self.frameContainer = FrameContainer(self.frameResource)
        # Creating Objects to frameContainerTop
        self.lbCombBox = tk.Label(self.__frameContainerTop, text="Language to get in:", font=("Helvetica", 10, "bold"), fg="black")
        self.lbCombBoxOut = tk.Label(self.__frameContainerTop, text="Language of out:", font=("Helvetica", 10, "bold"), fg="black")
        self.lbUrl = tk.Label(self.__frameContainerTop, text="Url:", font=("Helvetica", 10, "bold"), fg="black")
        self.lbLongSilence = tk.Label(self.__frameContainerTop, text="Silence:", font=("Helvetica", 10, "bold"), fg="black")
        self.lbDownFrequently = tk.Label(self.__frameContainerTop, text="Frequently:", font=("Helvetica", 10, "bold"), fg="black")

        self.txtVariableLS = tk.IntVar()
        self.txtVariableF = tk.IntVar()
        self.selectLanguage = tk.StringVar()
        self.selectLanguageOut = tk.StringVar()

        self.combBox = ttk.Combobox(self.__frameContainerTop, textvariable=self.selectLanguage,
                                    value=('Spanish', 'English', 'French'), state='readonly')
        self.combBoxOut = ttk.Combobox(self.__frameContainerTop, textvariable=self.selectLanguageOut,
                                    value=('Spanish', 'English', 'French'), state='readonly')
        self.enUrl = tk.Entry(self.__frameContainerTop, font=("Helvetica", 10, "bold"), fg="black")
        self.spLongSilence = tk.Spinbox(self.__frameContainerTop, from_=0, to=5000, textvariable=self.txtVariableLS)
        self.spLongSilence.delete(0, tk.END)
        self.spLongSilence.insert(0, str(2000))
        self.spDownFrequently = tk.Spinbox(self.__frameContainerTop, from_=-10000, to=5000, increment=1,
                                        textvariable=self.txtVariableF)
        self.spDownFrequently.delete(0, tk.END)
        self.spDownFrequently.insert(0, str(-100))
        # Creating Objects to frameContainerBo
        self.lbDataLoad = tk.Label(self.__frameContainerBo, text="File load:", font=("Helvetica", 10, "bold"),
                                fg="black",
                                bg="snow2")
        self.lbTime = tk.Label(self.__frameContainerBo, text="Time:", font=("Helvetica", 10, "bold"), fg="black",
                            bg="snow2")
        self.lbTimeStart = tk.Label(self.__frameContainerBo, text="Start Time:", font=("Helvetica", 10, "bold"),
                                    fg="black", bg="snow2")
        self.lbTimeEnd = tk.Label(self.__frameContainerBo, text="End Time:", font=("Helvetica", 10, "bold"), fg="black",
                                bg="snow2")

        self.lbDataLoadR = tk.Label(self.__frameContainerBo, text="0", font=("Helvetica", 10, "bold"), fg="black",
                                    bg="snow2")
        self.lbTimeR = tk.Label(self.__frameContainerBo, text="0", font=("Helvetica", 10, "bold"), fg="black",
                                bg="snow2")
        self.lbTimeStartR = tk.Label(self.__frameContainerBo, text="0", font=("Helvetica", 10, "bold"),
                                    fg="black", bg="snow2")
        self.lbTimeEndR = tk.Label(self.__frameContainerBo, text="0", font=("Helvetica", 10, "bold"),
                                fg="black", bg="snow2")
        # Adding objects to get in of window
        self.scrollingRight.pack(side=tk.RIGHT, fill=tk.Y)
        self.frameResource.pack(padx=5, pady=5, side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.__frameContainerTop.grid(row=0)
        self.frameContainer.grid(row=1, rowspan=50)
        self.__frameContainerBo.grid(row=51, column=0, columnspan=50)
        self.frameContainer.txtTranscription.configure(yscrollcommand=self.scrollingRight.set)

        # Adding objects to get in at frameContainerTop
        self.lbUrl.grid(row=0, column=2)
        self.lbLongSilence.grid(row=0, column=4)
        self.lbDownFrequently.grid(row=0, column=6)
        self.lbCombBox.grid(row=0, column=8)
        self.lbCombBoxOut.grid(row=0, column=10)

        self.enUrl.grid(row=2, column=2, padx=5, pady=10)
        self.spLongSilence.grid(row=2, column=4, padx=5, pady=10)
        self.spDownFrequently.grid(row=2, column=6, padx=5, pady=10)
        self.combBox.grid(row=2, column=8, padx=5, pady=10)
        self.combBoxOut.grid(row=2, column=10, padx=5, pady=10)
        # Adding objects to get in at frameContainerBo
        self.lbDataLoad.grid(row=0, column=1, padx=2, pady=10)
        self.lbTime.grid(row=0, column=3, padx=2, pady=10)
        self.lbTimeStart.grid(row=0, column=5, padx=2, pady=10)
        self.lbTimeEnd.grid(row=0, column=7, padx=2, pady=10)

        self.lbDataLoadR.grid(row=0, column=2, padx=5, pady=10)
        self.lbTimeR.grid(row=0, column=4, padx=5, pady=10)
        self.lbTimeStartR.grid(row=0, column=6, padx=5, pady=10)
        self.lbTimeEndR.grid(row=0, column=8, padx=5, pady=10)


class FrameContainer(tk.Frame):

    def __init__(self, master):
        super(FrameContainer, self).__init__(master)
        self.config(bg='snow2')
        # Creating Frames
        self.__frameContainerBT = tk.Frame(self, bg='snow2')
        self.__frameContainerTxt = tk.Frame(self, bg='red')
        # Creating Objects to frameContainerBT
        self.loadFileBT = tk.Button(self.__frameContainerBT, text="Load File", bg="DodgerBlue4", foreground="snow2",
                                    activeforeground="white",
                                    activebackground="DodgerBlue2", relief="ridge", font=("Helvetica", 12, "bold"),
                                    highlightcolor="black")
        self.downloadVBT = tk.Button(self.__frameContainerBT, text="Download Video", bg="DodgerBlue4",
                                    foreground="snow2",
                                    activeforeground="white", activebackground="DodgerBlue2", relief="ridge",
                                    font=("Helvetica", 12, "bold"), highlightcolor="black")
        self.writeFileLoad = tk.Button(self.__frameContainerBT, text="Write File Load", bg="DodgerBlue4",
                                    foreground="snow2",
                                    activeforeground="white", activebackground="DodgerBlue2", relief="ridge",
                                    font=("Helvetica", 12, "bold"), highlightcolor="black")
        self.speakAndWriteBT = tk.Button(self.__frameContainerBT, text="Speak And Write", bg="DodgerBlue4",
                                        foreground="snow2",
                                        activeforeground="white", activebackground="DodgerBlue2", relief="ridge",
                                        font=("Helvetica", 12, "bold"), highlightcolor="black")

        # Creating Objects to frameContainerTxt
        self.txtTranscription = tk.Text(self.__frameContainerTxt)

        # Adding Frames to get in the FrameContainer
        self.__frameContainerBT.pack(ipadx=5, ipady=5, side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.__frameContainerTxt.pack(ipadx=5, ipady=5, side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Adding objects to get in at frameContainerBT
        self.loadFileBT.pack(padx=10, pady=2, fill=tk.X, expand=True)
        self.downloadVBT.pack(padx=10, pady=2, fill=tk.X, expand=True)
        self.writeFileLoad.pack(padx=10, pady=2, fill=tk.X, expand=True)
        self.speakAndWriteBT.pack(padx=10, pady=2, fill=tk.X, expand=True)
        # Adding objects to get in at frameContainerTxt
        self.txtTranscription.pack(padx=2, pady=2, fill=tk.X, expand=True)


if __name__ == '__main__':
    # print('Enter the audio file path')
    # kindOf = "wav"
    # filePath = chooseFile(typ=kindOf)
    # print(filePath)
    # silence_based_conversion(path=filePath, typ=kindOf)
    c = Controller()
