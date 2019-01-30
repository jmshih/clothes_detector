import argparse
import cv2
import json
import numpy as np
import os
import sys

from detectron.utils.colormap import colormap
import detectron.utils.env as envu
import detectron.datasets.dummy_datasets as dummy_datasets

envu.set_up_matplotlib()
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description='script to visualize ground truth annotations')
    parser.add_argument('--annots', help='file containing annotations')
    parser.add_argument('--output', help='directory to which to output images')
    parser.add_argument('--imgdir', help='directory containing the images')
    return parser.parse_args()

def convert_json_to_cls(annots):
    clsformats = {}
    for ann in annots:
        bbox = ann['bbox']
        lbbox = [bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3]]
        if ann['image_id'] not in clsformats:
            clsformats[ann['image_id']] = [[] for i in range(6)]
        clsformats[ann['image_id']][ann['category_id']].append(lbbox)
    return clsformats

def convert_from_cls_format(cls_boxes):
    """Convert from the class boxes/segms/keyps format generated by the testing
    code.
    """
    box_list = [b for b in cls_boxes if len(b) > 0]
    if len(box_list) > 0:
        boxes = np.concatenate(box_list)
    else:
        boxes = None
    classes = []
    for j in range(len(cls_boxes)):
        classes += [j] * len(cls_boxes[j])
    return boxes, classes

def get_class_string(class_index, dataset):
    class_text = dataset.classes[class_index] if dataset is not None else \
        'id{:d}'.format(class_index)
    return class_text

def vis_one_image(
        im, im_name, output_dir, boxes, dpi=200, box_alpha=0.0, dataset=None, show_class=False,
        ext='pdf', out_when_no_box=False):
    """Visual debugging of detections."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if isinstance(boxes, list):
        boxes, classes = convert_from_cls_format(boxes)

    if (boxes is None or boxes.shape[0] == 0) and not out_when_no_box:
        return

    color_list = colormap(rgb=True) / 255

    cmap = plt.get_cmap('rainbow')

    fig = plt.figure(frameon=False)
    fig.set_size_inches(im.shape[1] / dpi, im.shape[0] / dpi)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.axis('off')
    fig.add_axes(ax)
    ax.imshow(im)

    if boxes is None:
        sorted_inds = [] # avoid crash when 'boxes' is None
    else:
        # Display in largest to smallest order to reduce occlusion
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        sorted_inds = np.argsort(-areas)

    mask_color_id = 0
    for i in sorted_inds:
        bbox = boxes[i, :4]

        # show box (off by default)
        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1],
                          fill=False, edgecolor='g',
                          linewidth=0.5, alpha=box_alpha))

        if show_class:
            ax.text(
                bbox[0], bbox[1] - 2,
                get_class_string(classes[i], dataset),
                fontsize=3,
                family='serif',
                bbox=dict(
                    facecolor='g', alpha=0.4, pad=0, edgecolor='none'),
                color='white')

    output_name = os.path.basename(im_name) + '.' + ext
    fig.savefig(os.path.join(output_dir, '{}'.format(output_name)), dpi=dpi)
    plt.close('all')

def main():
    args = parse_args()

    with open(args.annots) as jf:
        annotObj = json.load(jf)

    annots = annotObj['annotations']
    clsAnnots = convert_json_to_cls(annots)

    dummy_theyes_dataset = dummy_datasets.get_theyes_dataset()

    for img in clsAnnots:
        print(img)
        im_name = str(img)+'.jpg'
        impath = os.path.join(args.imgdir, im_name)
        im = cv2.imread(impath)
        vis_one_image(im[:, :, ::-1], im_name, args.output, clsAnnots[img],
                dataset=dummy_theyes_dataset,
                box_alpha=0.3,
                show_class=True,
                ext='jpg')

if __name__ == '__main__':
    sys.exit(main())
