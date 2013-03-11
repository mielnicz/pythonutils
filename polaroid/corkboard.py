#!/usr/bin/env python
#----------------------------------------------------------------------------
# 14-Feb-2013 ShaneG
#
#  This utility will convert images to a 'polaroid' style photo image with
#  an optional caption scrawled on the bottom. Requires the python imaging
#  library.
#----------------------------------------------------------------------------
from sys     import argv
from os.path import join, split, splitext, isfile, realpath, dirname
from random  import randint

# Names and properties of our resource files
RESOURCE_BACKGROUND = "background.jpg"

# Sizes and spacing
IMAGE_SPACING     = 0.025  # Spacing between images
IMAGE_SHADOW      = 0.025  # Size of image shadow
IMAGE_OFFSET      = 0.003  # Maximum random offset
IMAGE_ROTATION    = 15     # Maximum rotation
BACKGROUND_BORDER = 0.1    # Extra border around the background

# Colors
IMAGE_SHADOW_COLOR = ( 0, 0, 0, 64 )

# Layout sizes for various image counts
LAYOUTS = {
  3:  ( 2, 2 ), # Each entry is width, height
  4:  ( 2, 2 ),
  5:  ( 3, 2 ),
  6:  ( 3, 2 ),
  7:  ( 3, 3 ),
  8:  ( 3, 3 ),
  9:  ( 3, 3 ),
  10: ( 4, 3 ),
  11: ( 4, 3 ),
  12: ( 4, 3 ),
  }

#----------------------------------------------------------------------------
# Error reporting and usage information
#----------------------------------------------------------------------------

USAGE = """
Usage:

  corkboard.py image1 image2 image3 ... imageN

Where:

  image[1-N]  the images to position on the corkboard. There must be at
              least 3 images and no more than 12.

  The output is always placed in the file 'corkboard.jpg'.
"""

def showUsage():
  """ Show usage information and exit.
  """
  print USAGE
  exit(0)

def showError(msg):
  """ Show an error message and exit
  """
  print "Error: %s" % msg
  exit(1)

#----------------------------------------------------------------------------
# Resource helpers
#----------------------------------------------------------------------------

def getResourceFile(basefile):
  """ Get the fully qualified name of a resource file
  """
  return join(dirname(realpath(__file__)), basefile)

#----------------------------------------------------------------------------
# Image processing helpers
#----------------------------------------------------------------------------

# We need the python imaging library
try:
  from PIL import Image, ImageDraw, ImageFont
except:
  showError("This script requires PIL 1.1.7.")

def createBackground(width, height):
  """ Create the background image

    Creates the main background image by tiling the texture over it.
  """
  # Create the bare image
  corkboard = Image.new("RGB", (width, height))
  # Load our background image (needs to be tileable)
  try:
    background = Image.open(getResourceFile(RESOURCE_BACKGROUND))
    background.load()
  except:
    showError("Could not load background resource '%s'" % getResourceFile(RESOURCE_BACKGROUND))
  # Now tile it into the image
  x = 0
  while x < corkboard.size[0]:
    y = 0
    while y < corkboard.size[1]:
      corkboard.paste(background, (x, y))
      y = y + background.size[1]
    x = x + background.size[0]
  # Done
  return corkboard

def prepareImage(image, width, height, rotation):
  """ Prepare the image

    This creates a new image containing the original. It will be rotated by
    the angle given and a drop shadow will be added.
  """
  result = Image.new("RGBA", (width, height), (255, 255, 255, 0))
  ox = int((width - image.size[0]) / 2)
  oy = int((height - image.size[1]) / 2)
  sx = ox + int(image.size[0] * IMAGE_SHADOW)
  sy = oy + int(image.size[1] * IMAGE_SHADOW)
  # Add the drop shadow
  draw = ImageDraw.Draw(result)
  draw.rectangle((ox, oy, sx + image.size[0], sy + image.size[1]), fill = IMAGE_SHADOW_COLOR)
  # Add the original image
  result.paste(image, (ox, oy))
  # Do the rotation
  result = result.rotate(rotation, Image.BICUBIC, expand = True)
  # And we are done
  return result

#----------------------------------------------------------------------------
# Program entry point
#----------------------------------------------------------------------------

if __name__ == "__main__":
  # Check we have enough items on the command line
  if len(argv) < 4 or len(argv) > 13:
    showUsage()
  # Collect information about the files
  iw = 0
  ih = 0
  sources = list()
  for source in argv[1:]:
    name, ext = split(source)
    # Make sure we have an extension
    if len(ext) == 0:
      source = name + ".jpg"
    # Make sure the file exists
    if not isfile(source):
      showError("File '%s' does not exist" % source)
    # Now load it
    try:
      image = Image.open(source)
      image.load()
    except:
      showError("Unable to load file '%s'" % source)
    # Determine the size (and track the largest)
    iw = max(iw, image.size[0])
    ih = max(ih, image.size[1])
    # Add it to the list
    sources.append(image)
  # Adjust the image size to add the border
  iw = int(iw * (1.0 + IMAGE_SPACING))
  ih = int(ih * (1.0 + IMAGE_SPACING))
  # First, set up the background and border
  lw, lh = LAYOUTS[len(sources)]
  bw = int(BACKGROUND_BORDER * iw)
  bh = int(BACKGROUND_BORDER * ih)
  corkboard = createBackground((lw * iw) + (3 * bw), (lh * ih) + (3 * bh))
  # Now, add all the images to the corkboard
  locations = list()
  for image in sources:
    # Pick a location
    location = (randint(0, lw - 1), randint(0, lh - 1))
    while location in locations:
      location = (randint(0, lw - 1), randint(0, lh - 1))
    locations.append(location)
    # Prepare the source image
    image = prepareImage(image, iw, ih, randint(-IMAGE_ROTATION, IMAGE_ROTATION))
    # Prepare a random offset
    xo = int(iw * IMAGE_OFFSET)
    xo = randint(-xo, 0)
    yo = int(ih * IMAGE_OFFSET)
    yo = randint(-yo, 0)
    # Now add it to the final result
    if (location[0] == lw - 1) or (location[1] == lh - 1):
      # Don't apply offsets
      corkboard.paste(image, (location[0] * iw + bw, location[1] * ih + bh), image)
    else:
      corkboard.paste(image, (location[0] * iw + xo + bw, location[1] * ih + yo + bh), image)
  # And save the final result
  corkboard.save("corkboard.jpg")

