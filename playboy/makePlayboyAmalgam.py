# Generate amalgam from Playboy images.
#
# sample usage: python makePlayboyAmalgam.py '1980/*.jpg' '1990/*.jpg' -o two_decades_80s_90s.jpg 

import argparse, sys, glob, os
from PIL import Image

def vmap(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)

# array which indicates head-flops
headflops = (195404,195505,195612,195707,195907,
             196211,196308,
             197208,197402,197811,197907,
             198003,198011,198312,198512,198701,198910,
             199008,199108,199402,199501,1999905,
             200910,
             201206,201304,201402,201410,201509)

# get folder and options
parser = argparse.ArgumentParser(description='Find average aspect ratio of all images in a folder')
parser.add_argument('-fast', default=False,  action='store_true', help='Fast mode for testing')
parser.add_argument('-f', '--flip',   default=False,  action='store_true', help='Flip images to align heads')
parser.add_argument('-r', '--rotate',   default=False,  action='store_true', help='Rotate images to align heads')
parser.add_argument('-p', '--portraitonly',   default=False,  action='store_true', help='Only portrait images')
parser.add_argument('-l', '--landscapeonly',   default=False,  action='store_true', help='Only landscape images')
parser.add_argument('-e', '--equalize',   default=False,  action='store_true', help='Equalize RGB channels by individual normalization')
parser.add_argument('-w', '--width', type=int, default=400,  help='Output image width, default=%(default)s')
parser.add_argument('-ht', '--height', type=int, default=873,  help='Output image height, default=%(default)s')
parser.add_argument('-scale', '--scale', type=float, default=1,  help='Output scale, default=%(default)s')
parser.add_argument('-o', '--ofile', default='untitled.png', help='Output filename, default=%(default)s')
parser.add_argument('folder', nargs='+', help='Folder/glob to use')
args = parser.parse_args()

if (args.flip and args.rotate):
    print "-f and -r are mutually exclusive - pick one or none"
    sys.exit()
if (args.portraitonly and args.landscapeonly):
    print "-p  and -l are mutually exclusive - pick one or none"
    sys.exit()

if args.fast:
    args.scale = 0.5

args.width = int(args.width*args.scale+0.5)
args.height = int(args.height*args.scale+0.5)

num_pixels = args.width * args.height

# for each image in glob
sumw = 0
sumh = 0
nbr_images = 0
nbr_inliers = 0
nbr_outliers = 0

# create sum buffer here...
csums = [[0]*num_pixels for chan in range(3)]
num_images = 0

dst_aspect = args.height / float(args.width)


for globpath in args.folder:

    # if it's a directory, add /*.jpg
    if os.path.isdir(globpath):
        if globpath[-1] != '/':
            globpath += '/'
        globpath += '*.jpg'

    for name in glob.glob(globpath):
        print name,"..."
        # retrieve it and get it's size

        # !! choose correct image, based on args
        img = Image.open(name).convert("RGB")
        (w,h) = img.size

        # Let's work out tw,th (size of scaled image)
        if h > w:  # portrait

            src_aspect = h / float(w)
            if src_aspect > dst_aspect: # src image is taller, use existing width, and longer height (which will be cropped)
                print "taller"
                (tw,th) = (args.width,int(0.5+args.width*src_aspect))
            else: # src image is wider, use existing height and longer width (which will be cropped)
                print "wider %.4f -> %.4f (%d x %d)" % (dst_aspect, src_aspect, w, h)
                (tw,th) = (int(0.5+args.height/src_aspect), args.height)

            if args.landscapeonly:
                continue

        else:
            src_aspect = w / float(h)
            if src_aspect > dst_aspect: # rotated image is gonna be taller, use existing height and longer width
                print "flopped taller"
                (tw,th) = (int(0.5+args.width*src_aspect), args.width)
            else: # rotated image is gonna be wider, use existing width (which will become height) and longer height
                print "flopped wider"
                (tw,th) = (args.height,int(0.5+args.height/src_aspect))

            if args.portraitonly:
                continue


        img = img.resize((tw,th),Image.ANTIALIAS)
        # img.save("test_%d_s.png" % (num_images))

        # if image is landscape, rotate to portrait
        if (w > h):
            img = img.rotate(-90)
        # img.save("test_%d_sr.png" % (num_images))

        # if the head is flipped, deal with it
        (year,mon) = name.split('/')[-1].split('.')[0].split('_')
        key = int(str(year)+str(mon))
        if key in headflops:
            if args.flip:
                print "Flopping ",name
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            elif args.rotate:
                print "Rotating ",name
                img = img.rotate(180)


        # Then do a center crop, again, doing this first will speed up subsequent crops
        (w,h) = img.size
        (left,top,right,bottom) = ((w - args.width)/2, (h - args.height)/2, (args.width + w)/2, (args.height + h)/2)
        img = img.crop((left,top,right,bottom))
        # img.save("test_%d_src.png" % (num_images))



        # At this point all images are same size.  add images into sum buffer
        pixels = img.getdata()
        for ip,rgb in enumerate(pixels):
            if ip >= num_pixels:
                continue
            for chan in range(3):
                csums[chan][ip] += rgb[chan]

        del img

        num_images += 1

# determine min_val, max_val
min_val = [num_images*256,num_images*256,num_images*256]
max_val = [0,0,0]
for i in xrange(num_pixels):
    for chan in range(3):
        min_val[chan] = min(min_val[chan], csums[chan][i])
        max_val[chan] = max(max_val[chan], csums[chan][i])

if not args.equalize:
    min_val[0] = min(min_val)
    max_val[0] = max(max_val)

print "Min,max:",min_val,max_val

# normalize & render
oimg = Image.new("RGB",(args.width,args.height),"black") 
pixels = oimg.load()
if args.equalize:
    ip = 0
    for y in xrange(args.height):
        for x in xrange(args.width):
            # !! use individual channel values, if args.normalize
            pixels[x,y] = tuple(int(vmap(csums[chan][ip],min_val[chan],max_val[chan],0,255.99)) for chan in range(3))
            ip += 1
else:
    ip = 0
    min_v = min(min_val)
    max_v = max(max_val)
    for y in xrange(args.height):
        for x in xrange(args.width):
            # !! use individual channel values, if args.normalize
            pixels[x,y] = tuple(int(vmap(csums[chan][ip],min_v,max_v,0,255.99)) for chan in range(3))
            ip += 1

if args.landscapeonly:
    # spin it back...
    oimg = oimg.rotate(90)

# output the new image
oimg.save(args.ofile)
print "Output ",args.ofile
