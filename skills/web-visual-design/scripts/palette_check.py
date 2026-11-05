"""Check a palette tokens file for WCAG 2.2 contrast. Usage: palette_check.py <tokens.json>
Exit 0 = pass, 1 = problems found, 2 = unreadable file or bad usage."""
import json
import math
import re
import sys

MIN_RATIO = {"body": 4.5, "large": 3.0, "ui": 3.0}
_HEX = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})")
_NUM = r"[+-]?(?:\d+\.?\d*|\.\d+)"
_OKLCH = re.compile(rf"oklch\(\s*({_NUM})(%?)\s+({_NUM})\s+({_NUM})(?:deg)?\s*\)")
TOL = 0.001


def _encode(x):
    # linear -> sRGB transfer; sign kept so out-of-range values stay detectable
    s = -1 if x < 0 else 1
    x = abs(x)
    return s * (12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055)


def parse_color(value):
    if not isinstance(value, str):
        raise ValueError(f"not a string: {value!r}")
    v = value.strip()
    if m := _HEX.fullmatch(v):
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    if m := _OKLCH.fullmatch(v):
        L = float(m.group(1)) / (100 if m.group(2) else 1)
        C, H = float(m.group(3)), math.radians(float(m.group(4)))
        a, b = C * math.cos(H), C * math.sin(H)
        l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
        mm = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
        s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
        lin = (4.0767416621 * l - 3.3077115913 * mm + 0.2309699292 * s,
               -1.2684380046 * l + 2.6097574011 * mm - 0.3413193965 * s,
               -0.0041960863 * l - 0.7034186147 * mm + 1.7076147010 * s)
        rgb = tuple(_encode(c) for c in lin)
        if any(c < -TOL or c > 1 + TOL for c in rgb):
            raise ValueError(f"outside sRGB gamut: {value}")
        return tuple(min(1.0, max(0.0, c)) for c in rgb)
    raise ValueError(f"unsupported color: {value!r}")


def _luminance(rgb):
    r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _floor2(x):
    # truncate, never round up: 4.499 must not display as 4.50
    return f"{math.floor(x * 100) / 100:.2f}"


def _check_mode(name, mode):
    if not isinstance(mode, dict) or not isinstance(mode.get("colors"), dict):
        return [f"{name}: missing colors"]
    probs, colors = [], {}
    for k, v in mode["colors"].items():
        try:
            colors[k] = parse_color(v)
        except ValueError as e:
            probs.append(f"{name}: color {k}: {e}")
    if not 4 <= len(mode["colors"]) <= 6:
        probs.append(f"{name}: {len(mode['colors'])} colors, need 4 to 6")
    for p in mode.get("pairs") or []:
        fg, bg, use = p.get("fg"), p.get("bg"), p.get("use")
        if use not in MIN_RATIO:
            probs.append(f"{name}: unknown use {use!r} for {fg} on {bg}")
        elif fg not in colors or bg not in colors:
            probs.append(f"{name}: unknown or invalid color in pair {fg} on {bg}")
        else:
            r = contrast(colors[fg], colors[bg])
            if r < MIN_RATIO[use]:
                probs.append(f"{name}: {fg} on {bg} {use} {_floor2(r)} < {MIN_RATIO[use]:g}")
    return probs


def check(tokens):
    modes = tokens.get("modes") if isinstance(tokens, dict) else None
    modes = modes if isinstance(modes, dict) else {}
    probs = []
    for name in ("light", "dark"):
        if name not in modes:
            probs.append(f"{name}: mode missing")
        else:
            probs += _check_mode(name, modes[name])
    return probs


def main(argv):
    if len(argv) != 1:
        print("usage: palette_check.py <tokens.json>", file=sys.stderr)
        return 2
    try:
        with open(argv[0], encoding="utf-8-sig") as f:
            tokens = json.load(f)
    except (OSError, ValueError) as e:
        print(f"cannot read {argv[0]}: {e}", file=sys.stderr)
        return 2
    probs = check(tokens)
    for p in probs:
        print(p)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
