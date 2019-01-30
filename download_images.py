import argparse
import csv
import os
import sys
from urllib import request

def parse_args():
    parser = argparse.ArgumentParser(description='script to download images')
    parser.add_argument('--file', help='file containing image urls')
    parser.add_argument('--output', help='directory to which to write images')
    return parser.parse_args()

def main():
    args = parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    with open(args.file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            url = row[0]
            outfn = os.path.join(args.output, os.path.basename(url))
            if not os.path.exists(outfn):
                print(outfn)
                request.urlretrieve(url, filename=outfn)

if __name__ == '__main__':
    sys.exit(main())
