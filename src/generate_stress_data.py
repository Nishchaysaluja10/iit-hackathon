
import os
import random

DATA_DIR = "data/mini"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 1. Generate Long Book (approx 50KB)
book_path = os.path.join(DATA_DIR, "long_book.txt")
print(f"Generating {book_path}...")

chapters = []
for i in range(1, 21): # 20 Chapters
    chapter_content = f"Chapter {i}: The Journey Continues\n\n"
    # Filler text
    chapter_content += "The spaceship hummed with a low vibration. Captain Reynolds checked the navigation charts. " * 50
    # Specific facts for testing
    if i == 5:
        chapter_content += "On Stardate 4523.1, the crew discovered the Lost City of Zara. It was built of crystal and light. "
    if i == 10:
        chapter_content += "Lieutenant Commander Data (no relation) accidentally deleted the archives on Tuesday. "
    if i == 15:
        chapter_content += "The alien artifact was exactly 4.2 meters tall and vibrated at 400Hz. "
    
    chapter_content += "\nThere was silence in the void. " * 20
    chapters.append(chapter_content)

with open(book_path, "w") as f:
    f.write("\n".join(chapters))

# Remove sample_book.txt to avoid confusion
if os.path.exists(os.path.join(DATA_DIR, "sample_book.txt")):
    os.remove(os.path.join(DATA_DIR, "sample_book.txt"))

# 2. Generate Long Backstory CSV
csv_path = "data/test_mini.csv"
print(f"Generating {csv_path}...")

# Mix of True and False claims related to the specific facts above
backstory = """
1. Captain Reynolds commands the spaceship.
2. The crew discovered the Lost City of Zara on Stardate 4523.1.
3. The Lost City of Zara was built of mud and brick. (False)
4. Lieutenant Commander Data deleted the archives.
5. The archives were deleted on a Wednesday. (False - Tuesday)
6. The alien artifact was 4.2 meters tall.
7. The artifact vibrated at 400Hz.
8. The artifact was green. (False - Not mentioned)
9. The ship hummed with a high-pitched whine. (False - low vibration)
10. There are 20 chapters in this chronicle. (Inferred)
"""

with open(csv_path, "w") as f:
    f.write(f"character_name,backstory\nCaptain Reynolds,\"{backstory}\"")

print("Stress test data generated.")
