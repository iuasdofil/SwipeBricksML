import os


def main():
	files = os.listdir(os.getcwd())
	
	count = 0
	for file in files:
		if file.startswith("screenshot"):
			count += 1
	
	os.system("adb shell screencap -p /data/local/tmp/screenshot_%03d.png"%count)
	os.system("adb pull /data/local/tmp/screenshot_%03d.png"%count)


if __name__ == "__main__":
	main()