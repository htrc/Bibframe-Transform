import sys, os

def main():
	root_folder = sys.argv[1]
	for (dirpath, dirnames, filenames) in os.walk(sys.argv[1]):
		for filename in filenames:
			foldername = root_folder + (filename[:-4] if root_folder[-1:] == '/' else '/' + filename[:-4])
			os.mkdir(foldername)
#			print(filename)
#			print(root_folder + '/' + filename,foldername + '/' + filename)
			os.rename(root_folder + '/' + filename,foldername + '/' + filename)
			with open(foldername + '/' + filename + '.graph','w') as writefile:
				writefile.write('http://localhost:8890/DAV/')

main()