import argparse
from diary.core import Diary
from diary.search import strict_search

parser = argparse.ArgumentParser(description="Search a basic file-backed diary.")
parser.add_argument("file", type=str, help="filename")

args = parser.parse_args()
with open(args.file, "r") as f:
    diary = Diary.load(f)

print(diary.name)

while True:
    search_term = input("search:")
    for record in strict_search(diary, search_term):
        print(record)
