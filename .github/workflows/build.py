import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
RP = ROOT / "SAO_UI_RP"
BP = ROOT / "SAO_UI_BP"
DIST = ROOT / "dist"


def make_icon():
    # สร้างไอคอนไอเทม SAO Menu: วงกลมมืดกรอบฟ้า + เส้นและจุดสีส้ม
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((4, 4, size - 4, size - 4), fill=(10, 15, 24, 255),
              outline=(0, 212, 255, 255), width=4)
    d.line((16, 48, 48, 16), fill=(255, 138, 0, 255), width=6)
    d.ellipse((26, 26, 38, 38), fill=(255, 138, 0, 255))

    out = RP / "textures" / "items" / "sao_menu_item.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"[OK] icon -> {out.relative_to(ROOT)}")


def validate_json():
    # ตรวจว่าไฟล์ JSON ทุกไฟล์อ่านได้ ก่อนแพ็ก จะได้จับ error ตั้งแต่ตอน build
    for folder in (RP, BP):
        for path in folder.rglob("*.json"):
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as err:
                raise SystemExit(f"[ERROR] invalid JSON: {path.relative_to(ROOT)} -> {err}")
    print("[OK] all JSON files are valid")


def check_manifest(folder):
    if not (folder / "manifest.json").is_file():
        raise SystemExit(f"[ERROR] missing manifest.json in {folder.name}")


def zip_folder(src, dest):
    # manifest.json ต้องอยู่ระดับบนสุดของ zip จึงใช้ path ที่สัมพันธ์กับโฟลเดอร์ต้นทาง
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(src.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(src).as_posix())
    print(f"[OK] {dest.name}")


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    check_manifest(RP)
    check_manifest(BP)
    make_icon()
    validate_json()

    rp_pack = DIST / "SAO_UI_RP.mcpack"
    bp_pack = DIST / "SAO_UI_BP.mcpack"
    zip_folder(RP, rp_pack)
    zip_folder(BP, bp_pack)

    addon = DIST / "SAO_UI_Addon.mcaddon"
    with zipfile.ZipFile(addon, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(rp_pack, rp_pack.name)
        z.write(bp_pack, bp_pack.name)
    print(f"[OK] {addon.name}")


if __name__ == "__main__":
    main()
