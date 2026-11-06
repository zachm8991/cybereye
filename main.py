"""CyberEye: a local educational threat detection simulator."""
import argparse
import csv
import math
from collections import deque
from pathlib import Path
import pygame
from detector import Detector
from traffic import Traffic

W, H = 1200, 800
BG = (5, 10, 24)
CYAN = (65, 226, 255)
GREEN = (50, 235, 160)
RED = (255, 76, 113)
MUTED = (131, 155, 181)
PURPLE = (161, 104, 255)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frames', type=int, default=0, help='Exit after N frames (smoke test).')
    parser.add_argument('--screenshot', help='Save final frame to a PNG file.')
    args = parser.parse_args()
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('CyberEye | Network Threat Detection Simulator')
    clock = pygame.time.Clock()
    fonts = {n: pygame.font.SysFont('consolas', n) for n in (14, 16, 18, 24, 34)}
    traffic, detector = Traffic(), Detector()
    rows, alerts, archive = deque(maxlen=12), deque(maxlen=7), []
    total = frames = 0
    sim_time = accumulator = flash = 0.0
    paused = False
    notice = 'Ready. Press B or S to inject a simulated scenario.'
    buttons = [(pygame.Rect(36+i*285, 708, 270, 42), label, key)
               for i, (label, key) in enumerate([('B  BRUTE FORCE', 'brute'), ('S  PORT SCAN', 'scan'),
                                                ('SPACE  PAUSE / PLAY', 'pause'), ('E  EXPORT ALERTS', 'export')])]

    def text(value, x, y, color=CYAN, size=16):
        screen.blit(fonts[size].render(str(value), True, color), (x, y))

    def panel(rect, title):
        pygame.draw.rect(screen, (10, 23, 42), rect, border_radius=8)
        pygame.draw.rect(screen, (37, 97, 125), rect, 1, border_radius=8)
        text(title, rect.x+16, rect.y+12, size=18)
        pygame.draw.line(screen, (66, 49, 111), (rect.x+15, rect.y+40), (rect.right-15, rect.y+40))

    def action(key):
        nonlocal paused, notice
        if key == 'pause':
            paused = not paused
        elif key in ('brute', 'scan'):
            traffic.inject(key)
            notice = f'Queued simulated {key} scenario.'
        elif key == 'export':
            try:
                path = Path(__file__).resolve().parent / 'alerts.csv'
                with path.open('w', newline='', encoding='utf-8') as handle:
                    writer = csv.writer(handle)
                    writer.writerow(['simulation_seconds', 'type', 'source', 'reason'])
                    writer.writerows(archive)
                notice = f'Exported {len(archive)} alerts to alerts.csv'
            except OSError as exc:
                notice = f'Export failed: {exc}'[:120]

    running = True
    while running:
        dt = min(clock.tick(60)/1000, .1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                for code, key in [(pygame.K_b, 'brute'), (pygame.K_s, 'scan'),
                                  (pygame.K_SPACE, 'pause'), (pygame.K_e, 'export')]:
                    if event.key == code:
                        action(key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, _, key in buttons:
                    if rect.collidepoint(event.pos):
                        action(key)
        if not paused:
            sim_time += dt
            accumulator += dt
            flash = max(0, flash-dt)
            while accumulator >= .18:
                accumulator -= .18
                packet = traffic.next(sim_time)
                total += 1
                for kind, source, reason in detector.inspect(packet):
                    record = (round(sim_time, 1), kind, source, reason)
                    alerts.appendleft(record)
                    archive.append(record)
                    flash = 4
                rows.appendleft((packet, packet.source in detector.blocked))
        screen.fill(BG)
        for x in range(0, W, 32):
            pygame.draw.line(screen, (12, 24, 43), (x, 0), (x, H))
        for y in range(0, H, 32):
            pygame.draw.line(screen, (12, 24, 43), (0, y), (W, y))
        text('CYBEREYE', 36, 24, size=34)
        text('NETWORK THREAT DETECTION SIMULATOR', 260, 36, MUTED)
        text('PAUSED' if paused else 'SYSTEM ONLINE', 1010, 36, GREEN)
        color = RED if flash > 0 else CYAN
        cx, cy = 600, 205
        radius = int(99+4*math.sin(sim_time*2))
        pygame.draw.circle(screen, (12, 43, 62), (cx, cy), radius+18, 1)
        pygame.draw.circle(screen, color, (cx, cy), radius, 1)
        phase = sim_time*.4
        for i in range(24):
            a = i*math.tau/24 + phase
            pygame.draw.line(screen, color,
                             (cx+math.cos(a)*88, cy+math.sin(a)*88),
                             (cx+math.cos(a)*96, cy+math.sin(a)*96), 2)
        points = [(cx-150+300*i/80, cy-59*math.sin(math.pi*i/80)) for i in range(81)]
        points += [(cx+150-300*i/80, cy+59*math.sin(math.pi*i/80)) for i in range(81)]
        pygame.draw.polygon(screen, (8, 30, 48), points)
        pygame.draw.lines(screen, color, True, points, 2)
        iris = (cx+int(math.sin(sim_time)*12), cy)
        pygame.draw.circle(screen, RED if flash else PURPLE, iris, 48)
        for i in range(16):
            a = i*math.tau/16+phase
            pygame.draw.line(screen, (216, 206, 255),
                             (iris[0]+math.cos(a)*30, cy+math.sin(a)*30),
                             (iris[0]+math.cos(a)*44, cy+math.sin(a)*44), 2)
        pygame.draw.circle(screen, BG, iris, 25)
        pygame.draw.circle(screen, (245, 250, 255), (iris[0]-8, cy-9), 7)
        text('THREAT DETECTED' if flash else 'SIMULATED SURVEILLANCE ACTIVE', 438, 322, color, 18)
        for i, (title, value, detail) in enumerate([
            ('NETWORK STATISTICS', total, 'Synthetic packets generated'),
            ('DETECTION ENGINE', len(archive), 'Rule alerts triggered'),
            ('SIMULATED BLOCKLIST', len(detector.blocked), 'Sources flagged / no real blocking')]):
            rect = pygame.Rect(36+i*380, 365, 368, 104)
            panel(rect, title)
            text(value, rect.x+16, rect.y+48, GREEN, 24)
            text(detail, rect.x+65, rect.y+57, MUTED, 14)
        panel(pygame.Rect(36, 485, 690, 208), 'LIVE SYNTHETIC TRAFFIC')
        text('SOURCE IP          PORT   PROTO   STATUS', 52, 533, MUTED, 14)
        for i, (p, blocked) in enumerate(list(rows)[:8]):
            text(f'{p.source:<18} {p.port:<6} {p.protocol:<7} {"FLAGGED" if blocked else p.status}',
                 52, 553+i*16, RED if blocked or p.status == 'AUTH FAIL' else GREEN, 14)
        panel(pygame.Rect(742, 485, 422, 208), 'SECURITY ALERTS')
        if not alerts:
            text('No alerts. Inject a scenario below.', 758, 541, MUTED, 14)
        for i, (stamp, kind, source, reason) in enumerate(list(alerts)[:3]):
            text(f'{stamp:6.1f}s  {kind}  {source}', 758, 539+i*49, RED, 14)
            text(reason, 758, 557+i*49, MUTED, 14)
        for rect, label, _ in buttons:
            pygame.draw.rect(screen, (16, 47, 66) if rect.collidepoint(pygame.mouse.get_pos()) else (10, 26, 45), rect, border_radius=6)
            pygame.draw.rect(screen, CYAN, rect, 1, border_radius=6)
            text(label, rect.x+12, rect.y+12, size=16)
        text(notice, 36, 762, MUTED, 14)
        pygame.display.flip()
        frames += 1
        if args.frames and frames >= args.frames:
            running = False
    if args.screenshot:
        pygame.image.save(screen, args.screenshot)
    pygame.quit()

if __name__ == '__main__':
    main()
