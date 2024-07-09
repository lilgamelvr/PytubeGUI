import tkinter as tk
from tkinter import *
from tkinter import ttk
from pytube import YouTube
from tkinter import messagebox, filedialog
import os
import ffmpeg
import uuid
import re


def sanitize_filename(filename):
    # Remove any special characters that may cause issues in file paths
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def Widgets():
    head_label = Label(root, text="YouTube Video Downloader (Python Powered)",
                       padx=15,
                       pady=15,
                       font="SegoeUI 14",
                       bg="palegreen1",
                       fg="red")
    head_label.grid(row=1,
                    column=1,
                    pady=10,
                    padx=5,
                    columnspan=3)

    link_label = Label(root,
                       text="YouTube link :",
                       bg="salmon",
                       pady=5,
                       padx=5)
    link_label.grid(row=2,
                    column=0,
                    pady=5,
                    padx=5)

    root.linkText = Entry(root,
                          width=35,
                          textvariable=video_Link,
                          font="Arial 14")
    root.linkText.grid(row=2,
                       column=1,
                       pady=5,
                       padx=5,
                       columnspan=2)

    destination_label = Label(root,
                              text="Destination :",
                              bg="salmon",
                              pady=5,
                              padx=9)
    destination_label.grid(row=3,
                           column=0,
                           pady=5,
                           padx=5)

    root.destinationText = Entry(root,
                                 width=27,
                                 textvariable=download_Path,
                                 font="Arial 14")
    root.destinationText.grid(row=3,
                              column=1,
                              pady=5,
                              padx=5)

    browse_B = Button(root,
                      text="Browse",
                      command=Browse,
                      width=10,
                      bg="bisque",
                      relief=GROOVE)
    browse_B.grid(row=3,
                  column=2,
                  pady=1,
                  padx=1)

    resolution_label = Label(root,
                             text="Resolution :",
                             bg="salmon",
                             pady=5,
                             padx=5)
    resolution_label.grid(row=4,
                          column=0,
                          pady=5,
                          padx=5)

    resolution_menu = OptionMenu(root, resolution, *resolutions)
    resolution_menu.grid(row=4,
                         column=1,
                         pady=5,
                         padx=5)

    Download_B = Button(root,
                        text="Download Video",
                        command=Download,
                        width=20,
                        bg="thistle1",
                        pady=10,
                        padx=15,
                        relief=GROOVE,
                        font="Georgia, 13")
    Download_B.grid(row=5,
                    column=1,
                    pady=20,
                    padx=20)

    progress_label = Label(root,
                           text="Progress :",
                           bg="salmon",
                           pady=5,
                           padx=5)
    progress_label.grid(row=6,
                        column=0,
                        pady=5,
                        padx=5)

    root.progress = ttk.Progressbar(root, orient=HORIZONTAL, length=400, mode='determinate')
    root.progress.grid(row=6, column=1, pady=5, padx=5, columnspan=2)


def Browse():
    download_Directory = filedialog.askdirectory(
        initialdir="YOUR DIRECTORY PATH", title="Save Video")
    download_Path.set(download_Directory)


def Download():
    Youtube_link = video_Link.get()
    download_Folder = download_Path.get()
    selected_resolution = resolution.get()

    getVideo = YouTube(Youtube_link, on_progress_callback=progress_function)
    video_title = sanitize_filename(getVideo.title)

    if selected_resolution == "Highest":
        videoStream = getVideo.streams.filter(progressive=True).get_highest_resolution()
    elif selected_resolution == "Lowest":
        videoStream = getVideo.streams.filter(progressive=True).get_lowest_resolution()
    else:
        videoStream = getVideo.streams.filter(res=selected_resolution, progressive=True).first()

    if videoStream:
        root.progress['value'] = 0
        root.update_idletasks()
        videoStream.download(download_Folder, filename=str(uuid.uuid4()) + ".mp4")
        messagebox.showinfo("SUCCESSFULLY",
                            "DOWNLOADED AND SAVED IN\n"
                            + download_Folder)
    else:
        videoStream = getVideo.streams.filter(res=selected_resolution, mime_type="video/mp4").first()
        audioStream = getVideo.streams.filter(only_audio=True, mime_type="audio/mp4").first()

        if videoStream and audioStream:
            video_file_name = str(uuid.uuid4()) + ".mp4"
            audio_file_name = str(uuid.uuid4()) + ".mp4"

            video_file = os.path.join(download_Folder, video_file_name)
            audio_file = os.path.join(download_Folder, audio_file_name)

            root.progress['value'] = 0
            root.update_idletasks()
            videoStream.download(output_path=download_Folder, filename=video_file_name)
            audioStream.download(output_path=download_Folder, filename=audio_file_name)

            print(f"Video file: {video_file}")
            print(f"Audio file: {audio_file}")

            combined_file = os.path.join(download_Folder, video_title + ".mp4")

            video_input = ffmpeg.input(video_file)
            audio_input = ffmpeg.input(audio_file)
            ffmpeg.output(video_input, audio_input, combined_file).run(overwrite_output=True)

            os.remove(video_file)
            os.remove(audio_file)

            messagebox.showinfo("SUCCESSFULLY",
                                "DOWNLOADED AND SAVED IN\n"
                                + combined_file)
        else:
            messagebox.showerror("ERROR", "No stream available for the selected resolution")


def progress_function(stream, chunk, bytes_remaining):
    size = stream.filesize
    p = 100 - ((bytes_remaining / size) * 100)
    root.progress['value'] = p
    root.update_idletasks()


root = tk.Tk()
root.geometry("520x360")
root.resizable(False, False)
root.title("YouTube Video Downloader")
root.config(background="PaleGreen1")

video_Link = StringVar()
download_Path = StringVar()
resolution = StringVar(value="Highest")
resolutions = ["Highest", "Lowest", "144p", "240p", "360p", "480p", "720p", "1080p"]

Widgets()

root.mainloop()
