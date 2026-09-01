# Docker notes (this fork)

The image runs the files copied at **build** time. `start.sh` does **not** `git clone` or `git pull` on container start (the upstream script did, which overwrote the image and often failed on a non-empty `/app`).

## Build and run

```bash
docker build -t epson_print_conf .
docker run --name epson_print_conf -p 5990:5990 -e VNC_PASSWORD=1234 epson_print_conf
```

Connect a VNC client to `localhost:90` (display 90 = TCP port 5990).

- Override the password with `-e VNC_PASSWORD=...`.
- Do not publish port 5990 on an untrusted network.
- The default `1234` matches the previous README; change it for anything beyond a local test.
