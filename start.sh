#!/bin/bash
set -e

cd /app

echo "Starting Xvfb virtual display..."
Xvfb :99 -screen 0 1280x800x24 &

sleep 2

echo "Creating minimal Fluxbox config..."
mkdir -p ~/.fluxbox

cat > ~/.fluxbox/init <<'EOF'
session.screen0.toolbar.visible: false
session.screen0.slit.placement: BottomRight
session.screen0.slit.direction: Horizontal
session.screen0.fullMaximization: true
session.screen0.workspaces: 1
session.screen0.focusModel: sloppy
session.keyFile: ~/.fluxbox/keys
session.appsFile: ~/.fluxbox/apps
EOF

echo "Starting Fluxbox window manager..."
fluxbox -log ~/.fluxbox/fb.log 2>&1 &

sleep 2

echo "Starting VNC server..."
if [ -n "${VNC_PASSWORD:-}" ]; then
    mkdir -p ~/.vnc
    x11vnc -storepasswd "$VNC_PASSWORD" ~/.vnc/passwd
    x11vnc -display :99 -forever -rfbauth ~/.vnc/passwd -bg -rfbport 5990 -ncache 10 -ncache_cr &
else
    x11vnc -display :99 -forever -nopw -bg -rfbport 5990 -ncache 10 -ncache_cr &
fi

sleep 2

echo "Starting application. Connect via VNC to port 5990..."
exec python3 ui.py
