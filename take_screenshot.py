import os


def main():
	files = os.listdir(os.getcwd() + "/screenshot")
	
	count = 0
	for file in files:
		if file.startswith("screenshot") and file.endswith("png"):
			count += 1
	
	filename = "screenshot_%03d.png"%count
	
	os.system("adb shell screencap -p /data/local/tmp/"+filename)
	os.system("adb pull /data/local/tmp/"+filename)
	
	os.rename(filename, "screenshot/"+filename)
	
	print filename


if __name__ == "__main__":
	main()