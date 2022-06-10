import argparse
from diary.core import Diary

parser = argparse.ArgumentParser(
    description="Read the numbers tagged with a given name from a file-backed diary."
)
parser.add_argument("file", type=str, help="filename")
parser.add_argument("tag", type=str, help="tagname for the numbers")
parser.add_argument(
    "-v",
    "--verbose",
    help="Verbose, include the full diary entry as well",
    action="store_true",
)

args = parser.parse_args()
with open(args.file, "r") as f:
    diary = Diary.load(f)

print(diary.name)

for record in diary.records:
    if args.tag in record.numbers:
        print(record.timestamp, record.numbers[args.tag])
    if args.verbose:
        print(record)
