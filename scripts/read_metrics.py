import argparse
from diary.core import Diary

parser = argparse.ArgumentParser(
    description="Read the metrics tagged with a given name from a file-backed diary."
)
parser.add_argument("file", type=str, help="filename")
parser.add_argument("tag", type=str, help="tagname for the metrics")
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

for entry in diary.entries:
    if args.tag in entry.metrics:
        print(entry.timestamp, entry.metrics[args.tag])
    if args.verbose:
        print(entry)
