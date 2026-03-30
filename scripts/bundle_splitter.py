import os

# --- CONFIGURATION ---
INPUT_FILE = "sovereign_bundle.txt"
OUTPUT_DIR = "_use_ai_context"
CHUNK_SIZE = 250000  # Approx 250KB per chunk for optimal context handling

def split_bundle():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    file_num = 1
    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            
            output_filename = os.path.join(OUTPUT_DIR, f"sovereign_chunk_{file_num:03d}.txt")
            with open(output_filename, "w", encoding="utf-8") as out:
                out.write(chunk)
            
            print(f"📦 Created: {output_filename}")
            file_num += 1

    print(f"\n✅ Successfully split {INPUT_FILE} into {file_num-1} chunks in the '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    split_bundle()
