from pathlib import Path

root = Path(__file__).resolve().parents[1]
checks = {
    "server-2.1.8": 'VERSION = "2.1.8"' in (root / "api/index.py").read_text("utf-8"),
    "page-manager": (root / "api/page_runtime.py").is_file(),
    "page-manager-route": '/api/pages' in (root / "api/page_runtime.py").read_text("utf-8"),
    "admin-runtime-map": 'web/admin.html' in (root / "api/page_runtime.py").read_text("utf-8"),
    "chat-runtime-map": 'web/chat.html' in (root / "api/page_runtime.py").read_text("utf-8"),
    "extra-pages-discovery": 'runtime_pages/pages/' in (root / "api/page_runtime.py").read_text("utf-8"),
    "dev-push": 'push-dev' in (root / "api/page_runtime.py").read_text("utf-8"),
    "runtime-github-token": 'github-content-token.txt' in (root / "api/page_runtime.py").read_text("utf-8"),
    "index-source": (root / "runtime_pages/index.html").is_file(),
    "index-guard": (root / "api/page_runtime_guard.py").is_file(),
    "chat-ui-1.3.4": "UI_VERSION='1.3.4'" in (root / "web/chat_enhancements.js").read_text("utf-8"),
    "drawer-stack-repair": 'repairDrawerStack' in (root / "web/chat_enhancements.js").read_text("utf-8"),
    "version-receipt": 'swrlzVersionLine' in (root / "web/chat_enhancements.js").read_text("utf-8"),
}
failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + " | " + name)
print(f"RESULT | {len(checks)-len(failed)}/{len(checks)} PASS")
raise SystemExit(1 if failed else 0)
