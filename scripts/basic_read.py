import argparse
from diary.core import Diary

parser = argparse.ArgumentParser(description="Read a basic file-backed diary.")
parser.add_argument("file", type=str, help="filename")
parser.add_argument("--all", help="Spam all entries at once", action="store_true")

args = parser.parse_args()
with open(args.file, "r") as f:
    diary = Diary.load(f)

print(diary.name)

for entry in diary.entries:
    print(entry)
    if not args.all:
        input()
