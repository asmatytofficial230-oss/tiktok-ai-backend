import os
import librosa
import numpy as np
import streamlit as st
import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import yt_dlp

st.set_page_config(page_title="TikTok AI Studio", page_icon="🎬")

st.title("🎬 Complete AI TikTok Automation Studio")

url = st.text_input("Paste Video Link (YouTube / Facebook / Reels)")
target_duration = st.selectbox("Video Duration (Seconds)", [15, 30, 60], index=1)
enable_flip = st.checkbox("Flip Video Horizontally (Anti-Unoriginality)", value=True)
enable_hook = st.checkbox("Extract Peak Energy Clips (Smart Hook Cut)", value=True)
enable_ai_enhance = st.checkbox("Enable AI Visual & Color Enhancer", value=True)

if st.button("Process Video"):
    if not url:
        st.warning("Pehle video link daalein!")
    else:
        input_file = "raw_input.mp4"
        output_file = "viral_tiktok.mp4"
        audio_path = "temp_audio.wav"

        # Safe Cleanup
        for file in [input_file, output_file, audio_path]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': input_file,
            'overwrites': True,
            'quiet': True
        }

        with st.spinner("Video download aur edit ho rahi hai... Sabar karein..."):
            try:
                # 1. Download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                video = mp.VideoFileClip(input_file)

                # 2. Smart Hook Cuts
                if enable_hook and video.duration > target_duration:
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
                        if len(selected_starts) * chunk_len >= target_duration:
                            break

                    selected_starts.sort()
                    clips = [video.subclip(s, min(s + chunk_len, video.duration)) for s in selected_starts]
                    final_clip = mp.concatenate_videoclips(clips)
                elif video.duration > target_duration:
                    final_clip = video.subclip(0, target_duration)
                else:
                    final_clip = video

                # 3. Horizontal Flip
                if enable_flip:
                    final_clip = final_clip.fx(vfx.mirror_x)

                # 4. Color Enhancement
                if enable_ai_enhance:
                    final_clip = final_clip.fx(vfx.colorx, 1.15)
                    final_clip = final_clip.fx(vfx.lum_contrast, lum=5, contrast=0.1)

                # 5. Crop 9:16 Ratio
                w, h = final_clip.size
                target_w = int(h * (9/16))
                x1 = (w - target_w) // 2
                final_clip = final_clip.crop(x1=x1, width=target_w, height=h)

                # 6. Render
                final_clip.write_videofile(
                    output_file,
                    codec='libx264',
                    audio_codec='aac',
                    preset='ultrafast',
                    fps=30
                )

                # Close memory locks
                video.close()
                final_clip.close()

                # Display Output
                st.video(output_file)
                st.success("Video ready ho gayi hai!")

            except Exception as e:
                st.error(f"Error aaya: {str(e)}")
