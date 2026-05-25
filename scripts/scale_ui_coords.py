#!/usr/bin/env python3
"""从 main_page_coords_640.yaml 生成 480 屏坐标对照表（×0.75）。"""

from pathlib import Path

SCALE = 480 / 640
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "packages" / "main_page_coords_640.yaml"


def main() -> None:
    pairs: list[tuple[str, int]] = []
    for line in SRC.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("substitutions"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip().strip('"')
        if val.isdigit() or (val.startswith("-") and val[1:].isdigit()):
            pairs.append((key.strip(), int(val)))

    print(f"# scale = {SCALE:.4f}  (480/640)\n")
    print(f"{'key':<22} {'640':>6} {'480':>6}")
    print("-" * 38)
    for key, v640 in pairs:
        v480 = round(v640 * SCALE)
        print(f"{key:<22} {v640:>6} {v480:>6}")


if __name__ == "__main__":
    main()
