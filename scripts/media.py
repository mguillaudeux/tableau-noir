"""Exporte en MP4 et en GIF les animations du dossier (buts rejoués, figures animées).

    uv run --with playwright python scripts/media.py            # tout le dossier
    uv run --with playwright python scripts/media.py --fonts DIR  # polices locales (hors ligne)

Chaque animation est dessinée image par image dans web/studio.html (25 images par seconde, sans
dépendre de la vitesse de la machine), puis assemblée par ffmpeg : MP4 en H.264, GIF à 12 images
par seconde et 640 px de large. Les fichiers vont dans web/media/.
"""

from __future__ import annotations

import argparse
import base64
import functools
import http.server
import json
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import Route, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
FPS = 25
FONT_FILES = [
    ("Nothing You Could Do", "NothingYouCouldDo-Regular.ttf"),
    ("DM Mono", "DMMono-Regular.ttf"),
]


def serve() -> tuple[http.server.ThreadingHTTPServer, str]:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            pass

    srv = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(Quiet, directory=str(WEB))
    )
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def font_css(folder: Path) -> str:
    out = []
    for family, name in FONT_FILES:
        data = base64.b64encode((folder / name).read_bytes()).decode()
        out.append(
            f"@font-face{{font-family:'{family}';src:url(data:font/ttf;base64,{data}) "
            "format('truetype');}"
        )
    return "".join(out)


def encode(frames: Path, out: Path, ffmpeg: str) -> None:
    mp4 = out.with_suffix(".mp4")
    gif = out.with_suffix(".gif")
    subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "%05d.png"),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-movflags", "+faststart",
         str(mp4)],
        check=True,
    )  # fmt: skip
    palette = "fps=12,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=48[p];"
    subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-i", str(mp4), "-vf",
         palette + "[b][p]paletteuse=dither=bayer:bayer_scale=4", str(gif)],
        check=True,
    )  # fmt: skip


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", type=Path, help="dossier des polices .ttf (sinon Google Fonts)")
    ap.add_argument("--lang", default="fr")
    ap.add_argument("--chromium", help="chemin d'un Chromium déjà installé")
    args = ap.parse_args()
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    dossier = json.loads((WEB / "data" / "dossier.json").read_text(encoding="utf-8"))
    out_dir = WEB / "media"
    out_dir.mkdir(exist_ok=True)
    srv, base = serve()
    css = font_css(args.fonts) if args.fonts else None
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chromium)
        page = browser.new_page()
        if css:

            def fonts(route: Route) -> None:
                route.fulfill(status=200, body=css, content_type="text/css")

            page.route("https://fonts.googleapis.com/**", fonts)
        for item in dossier["media"]:
            q = f"match={dossier['match']}&lang={args.lang}&kind={item['kind']}"
            q += f"&minute={item['minute']}" if item["kind"] == "goal" else f"&race={item['race']}"
            page.goto(f"{base}/studio.html?{q}")
            page.wait_for_function("window.__studio !== undefined")
            duration = page.evaluate("window.__studio.duration")
            with tempfile.TemporaryDirectory() as tmp:
                n = int(duration * FPS) + 1
                for i in range(n):
                    url = page.evaluate(f"window.__studio.frame({i / FPS})")
                    png = base64.b64decode(url.split(",", 1)[1])
                    (Path(tmp) / f"{i:05d}.png").write_bytes(png)
                encode(Path(tmp), out_dir / item["file"], ffmpeg)
            print(item["file"], f"{duration:.1f} s")
        browser.close()
    srv.shutdown()


if __name__ == "__main__":
    main()
