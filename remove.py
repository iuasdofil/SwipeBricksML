import os

def main():
	os.chdir("crop_image")
	files = os.listdir(os.getcwd())
	
	for file in files:
		os.remove("/home/pw-1234/SwipeBricksML/crop_image/"+file)




if __name__ == "__main__":
	main()