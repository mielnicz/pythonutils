#!/usr/bin/env python
#----------------------------------------------------------------------------
# 14-Feb-2013 ShaneG
#
#  This utility will convert images to a 'polaroid' style photo image with
#  an optional caption scrawled on the bottom. Requires the python imaging
#  library.
#----------------------------------------------------------------------------
from sys     import argv
from os.path import join, split, splitext, isfile

# Names and properties of our resource files
RESOURCE_FONT      = "caption.ttf"
RESOURCE_FONT_SIZE = 142

# Image size constraints
IMAGE_SIZE   = 800
IMAGE_TOP    = 50
IMAGE_BOTTOM = 150
IMAGE_LEFT   = 50
IMAGE_RIGHT  = 50

BORDER_SIZE  = 3

# Colors
COLOR_FRAME   = (237, 243, 214)
COLOR_BORDER  = (0, 0, 0)
COLOR_CAPTION = (58, 68, 163)

# Font for the caption text
FONT_CAPTION = None

#----------------------------------------------------------------------------
# Error reporting and usage information
#----------------------------------------------------------------------------

USAGE = """
Usage:

  polaroid.py [options] source-image alignment [caption]

Where:

  source-image  name of the image file to transform. If no extension is
                specified .jpg is assumed.
  alignment     one of 'top', 'left', 'bottom', 'right' or 'center'. This
                specifies the portion of the image to include in the final
                output. 'top' and 'left' are synonomous as are 'bottom' and
                'right'.
  caption       If specified defines the caption to be displayed at the
                bottom of the image.

Available options are:

  --clockwise     Rotate the image clockwise before processing
  --anticlockwise Rotate the image anti-clockwise before processing
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
# Command line processing helpers
#----------------------------------------------------------------------------

def getOption(args):
  """ Check the argument list for an option (starting with '--').

    Returns the adjusted argument list and the option found.
  """
  if len(args) == 0:
    return None, args
  if args[0][:2] == "--":
    return args[0][2:], args[1:]
  return None, args

def getArgument(args):
  """ Get the next argument from the command line parameters

    Returns the adjusted argument list and the value of the argument.
  """
  if len(args) == 0:
    return None, args
  return args[0], args[1:]

#----------------------------------------------------------------------------
# Image processing helpers
#----------------------------------------------------------------------------

# We need the python imaging library
try:
  from PIL import Image, ImageDraw, ImageFont
except:
  showError("This script requires PIL 1.1.7.")

def rotateImage(source, rotation):
  """ Loads the named source image and rotates it appropriately.
  """
  image = Image.open(source)
  image.load()
  # Do the rotation needed
  if rotation == "clockwise":
    image = image.rotate(-90)
  elif rotation == "anticlockwise":
    image = image.rotate(90)
  return image

def scaleImage(image, align):
  """ Loads the named source image and crops and scales it. The return value
      is a new Image instance of the appropriate size.
  """
  # Do the cropping needed
  if image.size[0] > image.size[1]:
    if align in ("left", "top"):
      box = (0, 0, image.size[1], image.size[1])
    elif align in ("right", "bottom"):
      delta = image.size[0] - image.size[1]
      box = (delta, 0, image.size[0], image.size[1])
    elif align == "center":
      delta = (image.size[0] - image.size[1]) / 2
      box = (delta, 0, image.size[0] - delta, image.size[1])
    image = image.crop(box)
    image.load()
  elif image.size[1] > image.size[0]:
    if align in ("left", "top"):
      box = (0, 0, image.size[0], image.size[0])
    elif align in ("right", "bottom"):
      delta = image.size[1] - image.size[0]
      box = (0, delta, image.size[0], image.size[1])
    elif align == "center":
      delta = (image.size[1] - image.size[0]) / 2
      box = (0, delta, image.size[0], image.size[1] - delta)
    image = image.crop(box)
    image.load()
  # Should have a square image by here, rescale it
  if image.size[0] > IMAGE_SIZE:
    # Downsample
    image = image.resize((IMAGE_SIZE, IMAGE_SIZE), Image.ANTIALIAS)
  else:
    image = image.resize((IMAGE_SIZE, IMAGE_SIZE), Image.BICUBIC)
  return image

def addFrame(image):
  """ Adds the frame around the image
  """
  # Create the frame
  frame = Image.new("RGB", (IMAGE_SIZE + IMAGE_LEFT + IMAGE_RIGHT, IMAGE_SIZE + IMAGE_TOP + IMAGE_BOTTOM), COLOR_BORDER)
  # Create outer and inner borders
  draw = ImageDraw.Draw(frame)
  draw.rectangle((BORDER_SIZE, BORDER_SIZE, frame.size[0] - BORDER_SIZE, frame.size[1] - BORDER_SIZE), fill = COLOR_FRAME)
  draw.rectangle((IMAGE_LEFT - BORDER_SIZE, IMAGE_TOP - BORDER_SIZE, IMAGE_LEFT + IMAGE_SIZE + BORDER_SIZE, IMAGE_TOP + IMAGE_SIZE + BORDER_SIZE), fill = COLOR_BORDER)
  # Add the source image
  frame.paste(image, (IMAGE_LEFT, IMAGE_TOP))
  # All done
  return frame

def addCaption(image, caption):
  """ Add the caption to the image
  """
  if caption is None:
    return image
  # Write the text in place
  global FONT_CAPTION
  size = RESOURCE_FONT_SIZE
  width, height = FONT_CAPTION.getsize(caption)
  while ((width > IMAGE_SIZE) or (height > IMAGE_BOTTOM)) and (size > 0):
    size = size - 2
    FONT_CAPTION = ImageFont.truetype(RESOURCE_FONT, size)
    width, height = FONT_CAPTION.getsize(caption)
  if (size <= 0):
    showError("Caption is too large")
  # Add the caption to the image
  draw = ImageDraw.Draw(image)
  draw.text(((IMAGE_SIZE + IMAGE_LEFT + IMAGE_RIGHT - width) / 2, IMAGE_SIZE + IMAGE_TOP + ((IMAGE_BOTTOM - height) / 2)), caption, font = FONT_CAPTION, fill = COLOR_CAPTION)
  # All done
  return image

#----------------------------------------------------------------------------
# Program entry point
#----------------------------------------------------------------------------

if __name__ == "__main__":
  # Process the command line arguments
  options = { 'rotate': None }
  source = None
  target = None
  align = None
  caption = None
  # Do options first
  option, args = getOption(argv[1:])
  while option is not None:
    if option in ("clockwise", "anticlockwise"):
      options['rotate'] = option
    else:
      showError("Unrecognised option --%s" % option)
    option, args = getOption(args)
  # Now do other args
  source, args = getArgument(args)
  if source is None:
    showUsage()
  align, args = getArgument(args)
  if align is None:
    showUsage()
  caption, args = getArgument(args)
  if len(args) != 0:
    showUsage()
  # Verify the source file
  name, ext = splitext(source)
  if len(ext) == 0:
    source = name + ".jpg"
  if not isfile(source):
    showError("Source file '%s' does not exist." % source)
  # Generate the target file name
  target = name + ".polaroid.jpg"
  # Verify the alignment
  if not align in ("left", "right", "top", "bottom", "center"):
    showError("Unknown alignment '%s'." % align)
  # Prepare our resources
  fontName = join(split(argv[0])[0], RESOURCE_FONT)
  try:
    FONT_CAPTION = ImageFont.truetype(fontName, RESOURCE_FONT_SIZE)
  except:
    showError("Could not load resource '%s'." % fontName)
  # Now process the image
  sourceImage = rotateImage(source, options['rotate'])
  sourceImage = scaleImage(sourceImage, align)
  sourceImage = addFrame(sourceImage)
  sourceImage = addCaption(sourceImage, caption)
  # Save the result
  print(target)
  sourceImage.save(target)
