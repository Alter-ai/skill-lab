"""Self-check for skills/web-visual-design/scripts/palette_check.py. Run: python -I tests/test_palette_check.py"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "web-visual-design" / "scripts"))
import palette_check as pc  # noqa: E402

W, K = pc.parse_color("#FFFFFF"), pc.parse_color("#000000")
assert pc.contrast(W, K) == 21.0
assert pc.parse_color("#fff") == W
assert pc.contrast(pc.parse_color("#767676"), W) >= 4.5
assert pc.contrast(pc.parse_color("#777777"), W) < 4.5  # 4.48, must not round up to a pass
assert all(abs(x - 1) < 0.001 for x in pc.parse_color("oklch(1 0 0)"))
assert pc.parse_color("oklch(50% 0 0)") == pc.parse_color("oklch(0.5 0 0)")
for bad in ["#GGGGGG", "red", "#FFFFFF80", "oklch(0.5 0.1 200 / 50%)", "oklch(0.7 0.4 150)"]:
    try:
        pc.parse_color(bad)
    except ValueError:
        continue
    raise AssertionError(f"no ValueError for {bad}")

FOUR = {"bg": "#FFFFFF", "text": "#000000", "a": "#777777", "b": "#336699"}
OK_DARK = {"colors": {"bg": "#000000", "text": "#FFFFFF", "a": "#999999", "b": "#6699CC"},
           "pairs": [{"fg": "text", "bg": "bg", "use": "body"}]}


def mode(colors=None, pairs=None):
    return {"colors": colors or FOUR, "pairs": pairs if pairs is not None else [{"fg": "text", "bg": "bg", "use": "body"}]}


def toks(light, dark=OK_DARK):
    m = {"light": light}
    if dark is not None:
        m["dark"] = dark
    return {"modes": m}


assert pc.check(toks(mode())) == []
assert pc.check(toks(mode(pairs=[{"fg": "a", "bg": "bg", "use": "large"}]))) == []  # 4.48 >= 3
cases = {
    "low contrast": toks(mode(pairs=[{"fg": "a", "bg": "bg", "use": "body"}])),
    "unknown color": toks(mode(pairs=[{"fg": "nope", "bg": "bg", "use": "body"}])),
    "unknown use": toks(mode(pairs=[{"fg": "text", "bg": "bg", "use": "huge"}])),
    "missing dark": toks(mode(), dark=None),
    "3 colors": toks(mode(colors={"bg": "#FFFFFF", "text": "#000000", "a": "#777777"})),
    "7 colors": toks(mode(colors={f"c{i}": "#777777" for i in range(7)}, pairs=[])),
}
for name, t in cases.items():
    probs = pc.check(t)
    assert probs, name
    assert any(p.startswith(("light", "dark")) for p in probs), (name, probs)
low = pc.check(cases["low contrast"])
assert "4.47" in low[0] and "4.5" in low[0], low

with tempfile.TemporaryDirectory() as t:
    d = Path(t)
    good, badf = d / "good.json", d / "bad.json"
    good.write_text(json.dumps(toks(mode())), encoding="utf-8")
    badf.write_text(json.dumps(cases["low contrast"]), encoding="utf-8")
    bom = d / "bom.json"
    bom.write_bytes(b"\xef\xbb\xbf" + good.read_bytes())
    assert pc.main([str(good)]) == 0
    assert pc.main([str(badf)]) == 1
    assert pc.main([str(d / "missing.json")]) == 2
    assert pc.main([]) == 2
    assert pc.main([str(bom)]) == 0
print("ok")
