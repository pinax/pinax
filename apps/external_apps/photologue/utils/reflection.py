""" Function for generating web 2.0 style image reflection effects.

Copyright (c) 2007, Justin C. Driscoll
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of reflection.py nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

try:
    import Image
    import ImageColor
except ImportError:
    try:
        from PIL import Image
        from PIL import ImageColor
    except ImportError:
        raise ImportError("The Python Imaging Library was not found.")


def add_reflection(im, bgcolor="#00000", amount=0.4, opacity=0.6):
    """ Returns the supplied PIL Image (im) with a reflection effect

    bgcolor  The background color of the reflection gradient
    amount   The height of the reflection as a percentage of the orignal image
    opacity  The initial opacity of the reflection gradient

    Originally written for the Photologue image management system for Django
    and Based on the original concept by Bernd Schlapsi

    """
    # convert bgcolor string to rgb value
    background_color = ImageColor.getrgb(bgcolor)

    # copy orignial image and flip the orientation
    reflection = im.copy().transpose(Image.FLIP_TOP_BOTTOM)

    # create a new image filled with the bgcolor the same size
    background = Image.new("RGB", im.size, background_color)

    # calculate our alpha mask
    start = int(255 - (255 * opacity)) # The start of our gradient
    steps = int(255 * amount) # the number of intermedite values
    increment = (255 - start) / float(steps)
    mask = Image.new('L', (1, 255))
    for y in range(255):
        if y < steps:
            val = int(y * increment + start)
        else:
            val = 255
        mask.putpixel((0, y), val)
    alpha_mask = mask.resize(im.size)

    # merge the reflection onto our background color using the alpha mask
    reflection = Image.composite(background, reflection, alpha_mask)

    # crop the reflection
    reflection_height = int(im.size[1] * amount)
    reflection = reflection.crop((0, 0, im.size[0], reflection_height))

    # create new image sized to hold both the original image and the reflection
    composite = Image.new("RGB", (im.size[0], im.size[1]+reflection_height), background_color)

    # paste the orignal image and the reflection into the composite image
    composite.paste(im, (0, 0))
    composite.paste(reflection, (0, im.size[1]))

    # return the image complete with reflection effect
    return composite
