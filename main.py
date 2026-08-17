from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
import yt_dlp
import ffmpeg
import os
import moviepy.editor as mp
import librosa
import numpy as np

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TikTok AI Converter</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #0f172a; color: white; text-align: center; }
            input, select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: none; box-sizing: border-box; }
            input[type="text"] { background: #1e293b; color: white; }
            button { background: #2563eb; color: white; font-weight: bold; cursor: pointer; }
            .checkbox-group { text-align: left; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h2>AI TikTok Automation Studio</h2>
        <form action="/process" method="post">
            <input type="text" name="url" placeholder="Paste Video Link (YouTube/Reels/FB)" required>

            <label>Video Duration:</label>
            <select name="duration">
                <option value="15">15 Seconds</option>
                <option value="30" selected>30 Seconds</option>
                <option value="60">60 Seconds</option>
            </select>

            <div class="checkbox-group">
                <input type="checkbox" name="flip" value="true" id="flip" checked>
                <label for="flip">Flip Video Horizontally</label><br>
                <input type="checkbox" name="enhance" value="true" id="enhance" checked>
                <label for="enhance">Enable HD Quality Enhancer</label><br>
                <input type="checkbox" name="hook" value="true" id="hook" checked>
                <label for="hook">Smart AI Hook Cut (Extract Energetic Clips)</label>
            </div>

            <button type="submit">Process & Download</button>
        </form>
    </body>
    </html>
    """

@app.post("/process")
def process_video(
    url: str = Form(...),
    duration: int = Form(30),
    flip: bool = Form(False),
    enhance: bool = Form(False),
    hook: bool = Form(False)
):
    input_file = "raw_input.mp4"
    output_file = "processed_tiktok.mp4"

    if os.path.exists(input_file): os.remove(input_file)
    if os.path.exists(output_file): os.remove(output_file)

    ydl_opts = {'format': 'best', 'outtmpl': input_file, 'overwrites': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video = mp.VideoFileClip(input_file)

        if hook and duration > 0 and video.duration > duration:
            audio_path = "temp_audio.wav"
            video.audio.write_audiofile(audio_path, logger=None)
            y, sr = librosa.load(audio_path)
            rms = librosa.feature.rms(y=y)[0]

            frames_per_sec = len(rms) / video.duration
            top_indices = np.argsort(rms)[::-1]

            selected_starts = []
            chunk_len = 5
            for idx in top_indices:
                sec = idx / frames_per_sec
                if sec + chunk_len < video.duration and not any(abs(sec - s) < chunk_len for s in selected_starts):
                    selected_starts.append(sec)
                if len(selected_starts) * chunk_len >= duration:
                    break

            selected_starts.sort()
            clips = [video.subclip(s, min(s + chunk_len, video.duration)) for s in selected_starts]
            final_clip = mp.concatenate_videoclips(clips)
        elif duration > 0 and video.duration > duration:
            final_clip = video.subclip(0, duration)
        else:
            final_clip = video

        if flip:
            final_clip = final_clip.fx(mp.vfx.mirror_x)

        w, h = final_clip.size
        target_w = int(h * (9/16))
        x1 = (w - target_w) // 2
        final_clip = final_clip.crop(x1=x1, width=target_w, height=h)

        preset_mode = 'medium' if enhance else 'ultrafast'
        final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac', preset=preset_mode, fps=30)

        return FileResponse(output_file, media_type="video/mp4", filename="tiktok_viral.mp4")

    except Exception as e:
        return {"error": str(e)}
