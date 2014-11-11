Sample code for reproducing the Emergent Orange effect using uncorrelated photos from Flickr.

To use

1) Obtain an API key / shared secret from Flickr.  Store these in the file apikey.sh, which should read like so:


$api_key = '12d9e476f6ad2129db1598d51dbe8c03';
$sharedsecret = 'cce5b2335facb16b';

2) (optional) Use the script getHighestFlickrID.pl to obtain the highest ID currently in use on Flickr.  
Use this to modify the variable $maxID in getRandomPhotos.pl.

3) Create a directory cache/

4) Run the perl script getRandomPhotos.pl  - it will downlaod 10,000 random Flickr photo thumbnails to the cache.
   Note: This relies on the command-line version of curl being present.

5) Run the python script amalgamTest.py to produce test images using these random photos.  The default settings
produce a 10x10 grid of amalgam images.  Use the -p argument to increase the number of images to layer - as you 
increase the -p value, the orange effect will become more apparent.


    usage: amalgamTest.py [-h] [-r] [-n] [-o OFILE] [-p PASSES] [-d DIR] [-s SEED]

    optional arguments:

        -h, --help                       show this help message and exit
        -r, --random                     Enable random image generation - unimplemented
        -n, --nonormalize                Disable normalization
        -o OFILE, --ofile OFILE          Output image name
        -p PASSES, --passes PASSES       Passes (number of images to layer) - default 2
        -d DIR, --dir DIR                Image directory path (default .cache/)
        -s SEED, --seed SEED             Random seed - for reproduceable selections
        -v, --verbose                    Verbose output

Here is sample output, showing 100 images for each tile, with the output normalized.

