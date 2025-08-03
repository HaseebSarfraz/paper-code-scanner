# json_to_txt.py  ─ place anywhere inside your repo and run with:  python json_to_txt.py
import json, pathlib, glob

def convert_one(json_path: pathlib.Path):
    """
    Read one pairs.json ➜ write pairs.txt   (img_path<TAB>label per line)
    """
    txt_path = json_path.with_suffix(".txt")

    with json_path.open("r", encoding="utf8") as f:
        data = json.load(f)

    rows = []
    for entry in data:
        # PaddleOCR wants the path *relative to data_dir* and with forward slashes
        img_rel = entry["img_path"].replace("\\", "/")
        rows.append(f"{img_rel}\t{entry['label']}")

    txt_path.write_text("\n".join(rows), encoding="utf8")
    print(f"✓ wrote {txt_path}   ({len(rows)} samples)")


# ------------------------------------------------------------------
# Project‑root is the directory that contains 'model'.
convert_one(pathlib.Path("dev/pairs.json"))
# model/Dataset/json_to_txt.py
import json, pathlib

def convert_one(json_path: str | pathlib.Path, root: pathlib.Path):
    """Write root / <json‑name>.txt with rows  <rel-image-path>\t<label>"""
    json_path = pathlib.Path(json_path)
    txt_path  = json_path.with_suffix(".txt")

    rows = []
    with json_path.open("r", encoding="utf‑8") as f:
        for e in json.load(f):
            # make the path *relative to* data_dir (root)
            img_rel = (root / e["img_path"]).resolve().relative_to(root).as_posix()
            rows.append(f"{img_rel}\t{e['label']}")

    txt_path.write_text("\n".join(rows), encoding="utf‑8")
    print(f"✓ wrote {txt_path}  ({len(rows)} samples)")

if __name__ == "__main__":
    project   = pathlib.Path(__file__).resolve().parent          # …/model/Dataset
    convert_one("dev/pairs.json",   root=project / "dev")
    convert_one("train/pairs.json", root=project / "train")
