# CyberEye — Network Threat Detection Simulator

An original Python/Pygame educational project inspired by the supplied screenshot.
All traffic is generated locally. No packet capture, network scanning, real login
attempts, or firewall changes occur. The blocklist is simulated only.

## Windows: easiest start
1. Install Python 3.10 or newer from https://www.python.org/downloads/ (include the launcher).
2. Extract the entire ZIP. Do not run files from inside the ZIP.
3. Open the CyberEye folder and double-click START_WINDOWS.bat.
4. The first launch needs internet to install Pygame. Later launches use the same environment.

## Manual start (Windows)
Open a terminal in this folder:

    py -3 -m venv .venv
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    .venv\Scripts\python.exe main.py

## macOS / Linux

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python main.py

## Controls
- B / Brute Force button: queue ten fictional failed SSH logins.
- S / Port Scan button: queue connections to ten different fictional ports.
- Space: pause/resume simulation time and traffic.
- E: export the full alert history to alerts.csv beside main.py (overwrites previous export).
- Escape: exit.
Buttons work with a mouse too. Queued events process after resuming if paused.

## Detection rules
Each source has a rolling ten-second event window. Five authentication failures
trigger a brute-force alert; eight distinct destination ports trigger a port-scan
alert. Each source/rule has a ten-second alert cooldown. The animated eye turns red
for four seconds after an alert. A source remains on the simulated blocklist for
the rest of the session. Restart the program to reset everything.

## Files / concepts
- main.py: Pygame interface, event loop, animation, controls, CSV export.
- traffic.py: synthetic packet generation and queued attack scenarios.
- detector.py: Packet dataclass, deques, per-source rules and alert cooldown.
- test_detector.py: rule, expiry, cooldown, and normal-traffic checks.
- requirements.txt: dependency.
- START_WINDOWS.bat: local environment setup and launcher.

Run tests: python -m unittest -v test_detector

This is a teaching simulator, not a production intrusion detection system.
Threshold rules can produce false positives; no real AI/ML is used. No image,
font, sound, API key, or external asset files are required. Interface uses system
fonts and Pygame drawing primitives. A display at least 1200 x 800 is recommended.
