#!/bin/bash
set -euo pipefail

cd /app

echo "Starting Xvfb virtual display..."
Xvfb :99 -screen 0 1280x800x24 -ac +extension GLX +render -noreset &

# Wait until the X server is actually accepting connections
for _ in $(seq 1 40); do
    if xdpyinfo -display :99 >/dev/null 2>&1; then
        break
    fi
    sleep 0.25
done

echo "Creating minimal Fluxbox config..."
mkdir -p ~/.fluxbox

cat > ~/.fluxbox/init <<'FB'
# Minimal Fluxbox config for Docker/Xvfb
session.screen0.toolbar.visible: false
session.screen0.slit.placement: BottomRight
session.screen0.slit.direction: Horizontal
session.screen0.fullMaximization: true
session.screen0.workspaces: 1
session.screen0.focusModel: sloppy
session.keyFile: ~/.fluxbox/keys
session.appsFile: ~/.fluxbox/apps
FB

echo "Starting Fluxbox window manager..."
fluxbox -log ~/.fluxbox/fb.log >/dev/null 2>&1 &

sleep 1

VNC_PASSWORD="${VNC_PASSWORD:-1234}"
mkdir -p ~/.vnc
x11vnc -storepasswd "$VNC_PASSWORD" ~/.vnc/passwd >/dev/null

echo "Starting VNC server on TCP 5990 (VNC display :90)..."
x11vnc -display :99 -forever -rfbauth ~/.vnc/passwd -bg -rfbport 5990 -ncache 10 -ncache_cr

echo "Starting Tkinter application."
echo "Connect a VNC client to localhost:90 (port 5990)."
echo "Password is VNC_PASSWORD (default 1234). Override with docker run -e VNC_PASSWORD=..."
exec python3 ui.py
