import argparse
import json
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser(description='file to write out the image set from a coco dataset')
    parser.add_argument('--input', help='input file')
    parser.add_argument('--output', help='output file')
    return parser.parse_args()

def main():
    args = parse_args()

    with open(args.input) as jf:
        annotObj = json.load(jf)

    images = annotObj['images']
    with open(args.output, 'w') as of:
        for img in images:
            of.write('{}\n'.format(os.path.splitext(img['file_name'])[0]))

if __name__ == '__main__':
    sys.exit(main())
