import argparse
import csv
import json
import os
from PIL import Image
import sys

def parse_args():
    parser = argparse.ArgumentParser(description='file to convert bounding boxes to coco annotation format')
    parser.add_argument('--file', help='file containing the annotations')
    parser.add_argument('--output', help='file to which to output the reformatted annotations')
    parser.add_argument('--imgdir', help='directory containing the images')
    return parser.parse_args()

def main():
    args = parse_args()

    categories = {}
    images = {}

    annotObj = {
            'categories': [],
            'images': [],
            'annotations': [],
            'type': 'instances'
            }

    with open(args.file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            url = row[0]
            fn = os.path.basename(url)
            imgid = int(os.path.splitext(fn)[0])
            label = row[1]
            xmin = float(row[2])
            ymin = float(row[3])
            xmax = float(row[6])
            ymax = float(row[7])

            if label not in categories:
                categories[label] = {
                        'supercategory': 'none',
                        'id': len(categories) + 1,
                        'name': label
                        }

            width = None
            height = None
            if imgid not in images:
                im = Image.open(os.path.join(args.imgdir, fn))
                width, height = im.size
                images[imgid] = {
                        'file_name': fn,
                        'height': height,
                        'width': width,
                        'id': imgid
                        }
            else:
                width = images[imgid]['width']
                height = images[imgid]['height']

            xmin = round(xmin * width)
            ymin = round(ymin * height)
            xmax = round(xmax * width)
            ymax = round(ymax * height)

            bboxw = xmax - xmin
            bboxh = ymax - ymin
            area = bboxw * bboxh
            if bboxw < 0 or bboxh < 0:
                continue
            print('{} {} {}'.format(bboxw, bboxh, area))

            annotObj['annotations'].append({
                'ignore': 0,
                'iscrowd': 0,
                'bbox': [xmin, ymin, bboxw, bboxh],
                'segmentation': [],
                'image_id': imgid,
                'area': area,
                'id': len(annotObj['annotations']) + 1,
                'category_id': categories[label]['id']
                })

    annotObj['categories'] = [categories[x] for x in categories]
    annotObj['images'] = [images[x] for x in images]
    with open(args.output, 'w') as jf:
        json.dump(annotObj, jf, indent=2)

if __name__ == '__main__':
    sys.exit(main())
