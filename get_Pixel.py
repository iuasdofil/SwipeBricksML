import os
import numpy as np
from PIL import Image
import sys
import subprocess

heights = [364, 444, 524, 604, 684, 764, 844]
widths = [4, 124, 244, 364, 484, 604]

mid_h = [399, 479, 559, 639, 719, 799, 879]
mid_w = [59, 246, 299, 419, 539, 659]

width = 115
height = 75

# box = (364, 4, 364+height, 4+width)
box = (4, 364, 4+width, 364+height)

def main():
	img = Image.open(sys.argv[1])
	rgb = img.convert("RGB")
	rgb = np.array(rgb, np.uint8)
	rgb = np.reshape(rgb, (1280, -1, 3))
	
	arr = np.zeros((7, 6))
	
	print "start"
	
	for i in range(len(heights)):
		for j in range(len(widths)):
			r, g, b = rgb[heights[i]][widths[j]]
			# print "%d:%d >> %d %d %d"%(heights[i], widths[j], r, g, b)
			
			if r == 230 and g == 230 and b == 230:
				arr[i][j] = 0
			else:
				arr[i][j] = 1

			r, g, b = rgb[mid_h[i]][mid_w[j]]
			# print "%d:%d >> %d %d %d"%(mid_h[i], mid_w[j], r, g, b)
			if r == 58 and g == 211 and b == 97:
				arr[i][j] = -1
					
	print "print Box and Ball Position"
	for i in range(len(heights)):
		str = ""
		for j in range(len(widths)):
			str += "%02d "%arr[i][j]
			
		print str
		
	region = img.crop(box)
	region.save("crop_img.jpg")
			
if __name__ == "__main__":
	main()
	