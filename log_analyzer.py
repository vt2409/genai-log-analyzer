import os
import json
import subprocess

ERROR_CODE_FILE = 'error_codes.json'
LOG_FOLDER = 'logs'


def load_error_codes():
    if os.path.exists(ERROR_CODE_FILE):
        with open(ERROR_CODE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_error_codes(error_codes):
    with open(ERROR_CODE_FILE, 'w') as f:
        json.dump(error_codes, f, indent=2)


def explain_with_mistral(error_context):
    print("\n[🔎 Mistral is analyzing the unknown error...]")
    prompt = f"Explain this error: {error_context}"
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        explanation = result.stdout.strip()
        return explanation
    except Exception as e:
        return f"Failed to query Mistral: {e}"


def analyze_log(file_path, error_db):
    print(f"\n📄 Analyzing: {file_path}")
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if "ERROR" in line:
            matched_code = None
            print(f"error_db",error_db)
            for code in error_db:
                print(f"code : {code}")
                if code in line:
                    matched_code = code
                    break

            if matched_code:
                print(f"\n✅ Matched: {matched_code} ➤ {error_db[matched_code]}")
            else:
                explanation = explain_with_mistral(line)
                print(f"\n❓ Unknown error ➤ Mistral explanation:\n{explanation}")
                new_code = input("💾 Enter error code to save (or press Enter to skip): ").strip()
                if new_code:
                    error_db[new_code] = explanation
                    save_error_codes(error_db)
                    print(f"✅ Saved as {new_code}")


def main():
    error_db = load_error_codes()
    if not os.path.isdir(LOG_FOLDER):
        print(f"⚠️ No log folder found: {LOG_FOLDER}")
        return

    files = [f for f in os.listdir(LOG_FOLDER) if f.endswith(".txt")]
    if not files:
        print("⚠️ No log files found.")
        return

    for file in files:
        analyze_log(os.path.join(LOG_FOLDER, file), error_db)


if __name__ == '__main__':
    main()
