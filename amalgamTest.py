from PIL import Image, ImageDraw

# Amalgam Image Test (for Emergent Orange paper) -- Jim Bumgardner 8/21/2014
#
#
#
# version 1  8/21/2014 - partial port from ImageAveragingTest.pde (processing)

import argparse, glob, random, sys

defImagePath = "./cache"  # collection of 100x100 images (e.g. Flickr thumbnails)
                          # use getThumbnails.py to retrieve them

parser = argparse.ArgumentParser(description='Produce amalgam images using thumbnails')
# parser.add_argument('-m', '--mode', default='rgb', help='Mode: rgb,xyz,hsb,yiq') # !! unported 
parser.add_argument('-r', '--random', default=False,  action='store_true', help='Use random image generation')
parser.add_argument('-n', '--nonormalize', default=False,  action='store_true', help='Disable normalization')
parser.add_argument('-o', '--ofile', default='untitled.png',  help='Output image name')
parser.add_argument('-p', '--passes', default=2,  type=int, help='Passes (number of images to layer)')
parser.add_argument('-d', '--dir', default=defImagePath,  help='Image directory path')
parser.add_argument('-s', '--seed', default=0,  type=int, help='Random seed - for reproduceable selections')
parser.add_argument('-v', '--verbose', default=False,  action='store_true', help='Verbose output')

args = parser.parse_args()

gw,gh = (10,10)        # grid dimensions
numTiles = gw*gh
tw,th = (100,100)      # thumbnail dimension
numTPixels = tw*th     # number of pixels per thumb
dw,dh = (gw*tw,gh*th)  # output image dimensions

oimg = Image.new("RGB", (dw, dh), "black")

imageNames = glob.glob(args.dir + '/*.jpg')

print "%d image names loaded" % (len(imageNames))

if len(imageNames) == 0:
    print "No images found"
    sys.exit(0)

imgData = [ {'csums':[[0]*numTPixels for chan in range(3)]} for i in xrange(numTiles) ]

if args.seed > 0:
    random.seed(args.seed)

def vmap(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)

for p in xrange(args.passes):
    print "Pass",(p+1)
    for tileIdx in xrange(numTiles):
        if args.random:
            # produce randomly colored image here containing a randomly colored circle
            # these images don't display the bias in my testing
            #
            scale = 3 # we draw at 3x for antialiasing
            img = Image.new("RGB",(tw*scale,th*scale),"black") 
            draw = ImageDraw.Draw(img)
            draw.rectangle([0,0,tw*scale,th*scale],fill=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
            rad = random.randint(tw*scale/8,tw*scale/2)
            ex,ey = (random.randint(0,tw*scale),random.randint(0,th*scale))
            draw.ellipse([ex-rad,ey-rad,ex+rad,ey+rad],fill=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
            del draw
            img = img.resize((tw,th),Image.ANTIALIAS) # anti-alias
        else:
            while True: # load random image (keep trying until no error)
                iname = random.choice(imageNames)
                if args.verbose:
                    print "Loading",iname
                try:
                    img = Image.open(iname).convert("RGB").resize((tw,th),Image.ANTIALIAS)
                except:
                    print "Problem loading image",iname
                    continue
                break

        # !! convert to appropriate color space here...
        pixels = img.getdata()
        for ip,rgb in enumerate(pixels):
            if ip >= numTPixels:
                continue
            for chan in range(3):
                imgData[tileIdx]['csums'][chan][ip] += rgb[chan]
        del img


# produce normalization scale
minVal = args.passes*256
maxVal = 0
if not args.nonormalize:
    for tileIdx in xrange(numTiles):
        for i in xrange(numTPixels):
            for chan in range(3):
                minVal = min(minVal, imgData[tileIdx]['csums'][chan][i])
                maxVal = max(maxVal, imgData[tileIdx]['csums'][chan][i])
    print "Min->Max",minVal,maxVal
# produce output pixels

for tileIdx in xrange(numTiles):
    otile = Image.new("RGB",(tw,th),"black")
    pixels = otile.load()
    if args.nonormalize:
        # average
        ip = 0
        for y in xrange(th):
            for x in xrange(tw):
                pixels[x,y] = tuple(int(imgData[tileIdx]['csums'][chan][ip]/float(args.passes)) for chan in range(3))
                ip += 1
    else:
        # normalize
        ip = 0
        for y in xrange(th):
            for x in xrange(tw):
                pixels[x,y] = tuple(int(vmap(imgData[tileIdx]['csums'][chan][ip],minVal,maxVal,0,255.99)) for chan in range(3))
                ip += 1

    # !! convert back to appropriate colorspace here...

    # plot pixels on oimg
    ox = (tileIdx % gw)*tw
    oy = (tileIdx / gh)*th
    oimg.paste(otile, (ox,oy))

oimg.save(args.ofile)
print "Saved to",args.ofile
