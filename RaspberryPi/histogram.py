import sys
import time
from PIL import Image, ImageDraw

def get_luminance(r,g,b):
    return (r * .2126) + (g * .7152) + (b * .0722)

def generate_histogram(image,save_histogram=False):
    size = image.size
    occurances = {"red":[],"green":[],"blue":[]}
    for y in xrange(0,size[1]):
        for x in xrange(0,size[0]):
            pixel = image.getpixel((x,y))
            occurances["red"].append(pixel[0])
            occurances["green"].append(pixel[1])
            occurances["blue"].append(pixel[2])
    total_pixels = len(occurances["red"])
    output = list()
    for x in xrange(0,256):
        output.append(0)
    for x in xrange(0,total_pixels):
        lum = round(get_luminance(occurances["red"][x],occurances["green"][x],occurances["blue"][x]))
        index = int(lum)
        output[index] += 1
    max_value = 0
    non_zero_values = 0
    for each in output:
        if each > 0:
            non_zero_values += 1
        if each > max_value:
                max_value = each
    scale = float(100)/float(max_value)
    accumulator = 0
    lines = []
    for x in xrange(0,256):
        scaled_number = scale * float(output[x])
        line_length = int(scaled_number)
        lines.append(line_length)
        accumulator += line_length
    average = (accumulator/non_zero_values) / scale
    accumulator = 0
    for x in xrange(0,256):
        if output[x] > 0:
            variance = average - output[x]
            accumulator += variance ** 2
    variance = (accumulator/non_zero_values)
    if save_histogram:
        graph = Image.new("1",(256,100),1)
        draw = ImageDraw.Draw(graph)
        scale = float(100)/float(max_value)
        for x in xrange(0,256):
            draw.line((x,100,x,(100-lines[x])),fill=0)
        del draw
        graph.save("histogram.png","PNG")
        print "Saved histogram."
    return {"max":max_value,"histogram":output,"mean":average,"variance":variance}

def histogram_from_file(fp):
    image = Image.open(fp)
    return generate_histogram(image)
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            start = time.time()
            f = open(sys.argv[1],"rb")
            image = Image.open(f)
            histogram = generate_histogram(image,save_histogram=True)
            print "Analyzing %d pixels..." % (image.size[0] * image.size[1])
            print "Finished in %0.2f seconds." % (time.time() - start,)
            print(str(histogram))
            f.close()
        except IOError:
            print "Could not open sys.argv[1], perhaps it doesn't exist?" % sys.argv[1]
