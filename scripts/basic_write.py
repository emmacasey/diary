import argparse
from diary.core import Diary

parser = argparse.ArgumentParser(description="Write a basic file-backed diary.")
parser.add_argument("file", type=str, help="filename")
parser.add_argument("--create", help="create file on start", action="store_true")
parser.add_argument("--name", help="name for the diary if created")

args = parser.parse_args()

if args.create:
    diary = Diary(args.name or args.file, [])
else:
    with open(args.file, "r") as f:
        diary = Diary.load(f)

print(diary)

try:
    while True:
        text = input("Dear diary...\n")
        diary.add(text)
except KeyboardInterrupt:
    with open(args.file, "w") as f:
        diary.save(f)
