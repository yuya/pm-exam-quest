"""src/ の app.html にデータを埋め込み、1ファイル完結の index.html を作る。
使い方: python3 tools/build.py
"""
from pathlib import Path
root = Path(__file__).resolve().parent.parent
src = root / "src"
app = (src / "app.html").read_text(encoding="utf-8")
data = (src / "data_am2.js").read_text(encoding="utf-8") + "\n" + (src / "data_pm.js").read_text(encoding="utf-8")
assert "/*__DATA__*/" in app
(root / "index.html").write_text(app.replace("/*__DATA__*/", data, 1), encoding="utf-8")
print("built index.html")
