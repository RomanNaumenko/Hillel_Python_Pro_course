from PIL import Image
import os



baseheight = 512
basewidth = 512


def resize(infile):
    file, ext = os.path.splitext(infile)
    with Image.open(infile) as im:
        res_image = im.resize((basewidth, baseheight), Image.ANTIALIAS)
        res_image.mode = 'RGB'
        res_image.save(file + '_resized.jpg', 'JPEG')


if __name__ == '__main__':
    resize('uploads79_1.png')
