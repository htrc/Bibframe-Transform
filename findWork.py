import sys, os, mmap

def searchFiles():
	folder_name = '/Users/dkudeki-admin/Documents/GitHub/Bibframe-Transform/trimmed_all_volumes_json_BIBF_records'
	for root, dirs, files in os.walk(folder_name):
		for f in files:
			if '.xml' in f:
				file_path = folder_name + '/' + f[5:-5].replace('_segment','') + '/' + f
				try:
					with open(file_path,'rb') as readfile:
						stream = mmap.mmap(readfile.fileno(),0,access=mmap.ACCESS_READ)
						if stream.find(b'http://hdl.handle.net/2027/uc2.ark:/13960/t0zp4br0w') != -1:
							print("FOUND in " + file_path)
				except IOError:
					print("File does not exist: " + file_path)

searchFiles()