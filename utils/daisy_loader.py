import json
import os

# Path ke folder data (Pastikan fail JSON ada dalam folder 'data/')
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
    # Memuatkan naskhah novel ATMA
    return load_json_file("daisy_novel.json")

def load_arkib():
    # Memuatkan monolog watak
    return load_json_file("daisy_arkib.json")

def load_rahsia():
    # Memuatkan tips penulisan
    return load_json_file("daisy_rahsia.json")