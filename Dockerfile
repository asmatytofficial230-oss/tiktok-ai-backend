FROM python:3.10-slim

# System tools & FFmpeg install
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pehle sara code COPY karein taake subfolders ya path issue khatam ho jaye
COPY . /app/

# Requirements install karein
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# Streamlit run karein
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
