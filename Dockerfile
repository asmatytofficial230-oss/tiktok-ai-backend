FROM python:3.10-slim

# FFmpeg aur zaroori system tools install karein
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code copy karein
COPY . .

EXPOSE 8501

# Streamlit run karein
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
