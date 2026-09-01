# Use the official Python slim image
FROM python:3.11-slim

# Install system dependencies including Tkinter, Xvfb, and X11 utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    tk \
    tcl \
    libx11-6 \
    libxrender1 \
    libxext6 \
    libxinerama1 \
    libxi6 \
    libxrandr2 \
    libxcursor1 \
    libxtst6 \
    tk-dev \
    xvfb \
    x11-apps \
    x11vnc \
    fluxbox \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Official python images use their own pip; no --break-system-packages needed
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the rest of the app (see .dockerignore)
COPY . .

# Set the DISPLAY environment variable for Xvfb
ENV DISPLAY=:99

# Default VNC password — override at runtime with -e VNC_PASSWORD=...
ENV VNC_PASSWORD=1234

# Expose the VNC port (display :90 => 5900+90)
EXPOSE 5990

ENTRYPOINT ["bash", "/app/start.sh"]
