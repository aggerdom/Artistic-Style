import numpy as np
import pathlib
from PIL import Image
from collections import namedtuple
from operator import itemgetter
from seggui import ControlPanel, filedialog
import argparse
import sys
if len(sys.argv) > 1:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_image_path", type=str, help="Path to the image to be chopped up")
    parser.add_argument("width",type=int,default=512,help="Width of full-size image segments")
    parser.add_argument("height",type=int,default=512,help="Height of full-size image segments")
    parser.add_argument('-d','--dropexcess', action='store_true',
                        help="If -d switch is used, non-full-sized images will be dropped from the output")
    parser.add_argument('-o', "--output", nargs='?', help='Path to folder to output the image segments to')
    script_args = parser.parse_args()
else:
    from functools import partial
    panel = ControlPanel()
    panel.add_filepath_chooser('input_image_path',
                               op=partial(filedialog.askopenfilename,
                                          initialdir='./',
                                          title= "Folder to save the image segments to"))
    panel.add_entry('width','width')
    panel.add_entry('height','height')
    panel.add_folder_chooser('-o','Output Folder', op=filedialog.askdirectory)
    panel.add_checkbox('-d','Drop Small Segments',default=0)
    script_args = panel.mainloop()
    for key in ('width','height'):
        script_args[key] = int(script_args[key])




def decompose(img, main_width=512, main_height=512):
    """
    :param img: Image to be decomposed
    :type img: PIL Image
    :param main_width: width of full size (non excess) segments
    :type main_width: int
    :param main_height: heigh of full size (non excess) segments
    :type main_height: int
    :return: Dictionary of segments of form {(row_number, column_number): Image}
    :rtype: dict
    """
    segments = {}  # cropped images with keys (row,column)
    owidth, oheight = img.size
    nrows = owidth // main_width
    ncols = oheight // main_height
    right_excess = owidth - (ncols * main_width)
    bottom_excess = oheight - (nrows * main_height)
    for r_i in range(nrows):
        for c_i in range(ncols):
            left = c_i * main_width
            right = (c_i + 1) * main_width
            upper = (r_i * main_height)
            lower = (r_i + 1) * main_height
            segments[(r_i, c_i)] = img.crop((left, upper, right, lower))
        if right_excess != 0 and not script_args["-d"]:
            c_i += 1
            left += main_width
            right = owidth
            segments[(r_i, c_i)] = img.crop((left, upper, right, lower))
    if bottom_excess != 0 and not script_args["-d"]:
        r_i += 1
        for c_i in range(ncols):
            left = c_i * main_width
            right = (c_i + 1) * main_width
            upper = (r_i * main_height)
            lower = oheight
            segments[(r_i, c_i)] = img.crop((left, upper, right, lower))
        if right_excess != 0:
            c_i += 1
            left += main_width
            right = owidth
            segments[(r_i, c_i)] = img.crop((left, upper, right, lower))
    return segments

def show_segments(segment_dict):
    for k,seg in sorted(segs.items(),key=itemgetter(0,1)):
        seg.show()

from os import path
def save_segments(segment_dict,savedirectory):
    for k, seg in sorted(segs.items(), key=itemgetter(0, 1)):
        r, c = k
        output_fname = path.join(savedirectory,
                                    '{base}-burst-row{r}-col-{c}.jpg'.format(base=pathlib.Path(img.filename).stem, r=r, c=c))
        # output_fname = './burst1/{base}-burst-row{r}-col-{c}.jpg'.format(base=pathlib.Path(img.filename).stem, r=r, c=c)
        seg.save(output_fname, format='jpeg')

def testing_show():
    img = Image.open('./examples/1.jpg')
    segs = decompose(img, 100, 100)
    show_segments(segs)

def testing_save():
    img = Image.open('./examples/1.jpg')
    segs = decompose(img, 100, 100)
    save_segments(segs)

if __name__ == '__main__':
    img = Image.open(script_args['input_image_path'])
    segs = decompose(img,
                     script_args['width'],
                     script_args['height'])
    save_segments(segs, script_args['-o'])


