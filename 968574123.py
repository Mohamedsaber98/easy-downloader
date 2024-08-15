import os
import re
import threading
import yt_dlp
import requests
import tkinter as tk
from tkinter import ttk, messagebox

# Constants
OUTPUT_PATH = "/storage/emulated/0/Download"
API_KEY = "YOUR_YOUTUBE_API_KEY_HERE"

def is_valid_url(url):
    return re.match(r'^https?://', url) is not None

def progress_hook(d, url, lock, update_progress):
    if d['status'] == 'downloading':
        percentage = d.get('_percent_str', '0.0%').strip('%')
        try:
            percentage = float(percentage)
            status = f"Downloading {url}... {percentage:.1f}%"
            update_progress(percentage, status)
        except ValueError:
            pass
    elif d['status'] == 'finished':
        update_progress(100, f"Download completed for {url}!")

def download(url, format_choice, lock, update_progress):
    ydl_opts = {
        'format': format_choice,
        'outtmpl': os.path.join(OUTPUT_PATH, '%(title)s.%(ext)s'),
        'progress_hooks': [lambda d: progress_hook(d, url, lock, update_progress)],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        update_progress(0, f"An error occurred: {e}")

def search_videos(query):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("items", [])
        # هنا يمكنك عرض النتائج في نافذة Tkinter جديدة إذا كنت ترغب
    else:
        # تعامل مع حالة الخطأ
        pass

class EasyDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Easy Downloader")
        self.root.geometry("300x400")  # تصغير حجم النافذة
        self.lock = threading.Lock()

        # تعديل الألوان والخطوط
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white", font=("Arial", 12))
        style.configure("TButton", background="lightgreen", font=("Arial", 10, "bold"))
        style.configure("TEntry", font=("Arial", 10), padding=5)

        # الواجهة الرئيسية
        self.frame = ttk.Frame(root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # عنوان التطبيق
        title = ttk.Label(self.frame, text="Easy Downloader", font=("Arial", 13, "bold"), background="yellow")
        title.grid(row=0, column=0, columnspan=2, pady=5)

        # حقل البحث
        self.search_entry = ttk.Entry(self.frame, width=20)
        self.search_entry.grid(row=1, column=0, pady=5, sticky=tk.W)
        search_button = ttk.Button(self.frame, text="Search", command=self.on_search)
        search_button.grid(row=1, column=1, pady=5, sticky=tk.W)

        # حقل إدخال URL
        self.url_entry = ttk.Entry(self.frame, width=20)
        self.url_entry.grid(row=2, column=0, pady=5, sticky=tk.W)
        url_label = ttk.Label(self.frame, text="Enter URL(s):", background="yellow")
        url_label.grid(row=2, column=1, pady=5, sticky=tk.W)

        # أزرار خيارات التنزيل
        mp4_button = ttk.Button(self.frame, text="Download MP4", command=lambda: self.on_choice_selected("MP4"))
        mp4_button.grid(row=3, column=0, pady=5, sticky=tk.W)

        mp3_button = ttk.Button(self.frame, text="Download MP3", command=lambda: self.on_choice_selected("MP3"))
        mp3_button.grid(row=3, column=1, pady=5, sticky=tk.W)

        playlist_button = ttk.Button(self.frame, text="Download Playlist", command=self.on_playlist_download)
        playlist_button.grid(row=4, column=0, pady=5, sticky=tk.W)

        # شريط التقدم
        self.progress_bar = ttk.Progressbar(self.frame, orient="horizontal", length=250, mode="determinate")
        self.progress_bar.grid(row=5, column=0, columnspan=2, pady=10, sticky=tk.W)

        # تسمية التقدم
        self.progress_label = ttk.Label(self.frame, text="", background="white")
        self.progress_label.grid(row=6, column=0, columnspan=2, pady=5, sticky=tk.W)

    def on_choice_selected(self, choice):
        video_urls = self.url_entry.get().split(',')
        if any(not is_valid_url(url.strip()) for url in video_urls):
            messagebox.showerror("Error", "Please enter valid URLs.")
            return

        format_choice = 'bestvideo+bestaudio/best' if choice == "MP4" else 'bestaudio'
        for url in video_urls:
            url = url.strip()
            if is_valid_url(url):
                threading.Thread(target=self.download_thread, args=(url, format_choice)).start()

    def on_playlist_download(self):
        playlist_url = self.url_entry.get()
        if not is_valid_url(playlist_url):
            messagebox.showerror("Error", "Please enter a valid URL.")
            return
        threading.Thread(target=self.download_thread, args=(playlist_url, 'bestvideo+bestaudio/best')).start()

    def on_search(self):
        query = self.search_entry.get()
        if query:
            threading.Thread(target=search_videos, args=(query,)).start()
        else:
            messagebox.showerror("Error", "Please enter a search query.")

    def download_thread(self, url, format_choice):
        download(url, format_choice, self.lock, self.update_progress)

    def update_progress(self, percentage, status):
        self.progress_bar["value"] = percentage
        self.progress_label.config(text=status)

if __name__ == "__main__":
    root = tk.Tk()
    app = EasyDownloaderApp(root)
    root.mainloop()