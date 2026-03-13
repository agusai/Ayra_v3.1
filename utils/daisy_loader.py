import json
import os

# Path ke folder data
DATA_DIR = "data"

def load_json_file(filename):
    path = os.path.join(DATA_DIR, filename)
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"error": f"Fail {filename} tidak dijumpai."}
    except Exception as e:
        return {"error": str(e)}

def load_novel():
    return load_json_file("daisy_novel.json")

def load_arkib():
    return load_json_file("daisy_arkib.json")

def load_rahsia():
    return load_json_file("daisy_rahsia.json")


def build_daisy_context(max_novel_chars=3000, max_arkib_chars=2000, max_rahsia_chars=800):
    """
    Build a structured context string from all three JSON files.
    Safe truncation supaya tak overflow Gemini context.
    """
    novel_data = load_novel()
    arkib_data = load_arkib()
    rahsia_data = load_rahsia()

    # ── Novel: ambil chapters content sahaja ──
    novel_str = ""
    if "chapters" in novel_data:
        for ch in novel_data["chapters"]:
            chunk = f"[Bab {ch.get('number','')} - {ch.get('title','')}]\n{ch.get('content','')}\n\n"
            if len(novel_str) + len(chunk) > max_novel_chars:
                break
            novel_str += chunk
    else:
        novel_str = json.dumps(novel_data, ensure_ascii=False)[:max_novel_chars]

    # ── Arkib: nama + role + monolog pertama setiap watak ──
    arkib_str = ""
    if "characters" in arkib_data:
        for char in arkib_data["characters"]:
            monolog = char.get("monologues", [{}])[0].get("content", "")
            chunk = f"[{char.get('name','')} — {char.get('role','')}]\n{char.get('description','')}\nMonolog: {monolog}\n\n"
            if len(arkib_str) + len(chunk) > max_arkib_chars:
                break
            arkib_str += chunk
    else:
        arkib_str = json.dumps(arkib_data, ensure_ascii=False)[:max_arkib_chars]

    # ── Rahsia: philosophy + lessons ──
    rahsia_str = ""
    if "master_direction" in rahsia_data:
        rahsia_str += f"Falsafah: {rahsia_data['master_direction'].get('philosophy','')}\n"
        rahsia_str += f"Gaya: {rahsia_data['master_direction'].get('teaching_style','')}\n\n"
    if "lessons" in rahsia_data:
        for lesson in rahsia_data["lessons"]:
            chunk = f"[{lesson.get('title','')}] {lesson.get('instruction','')}\n"
            if len(rahsia_str) + len(chunk) > max_rahsia_chars:
                break
            rahsia_str += chunk

    return novel_str.strip(), arkib_str.strip(), rahsia_str.strip()