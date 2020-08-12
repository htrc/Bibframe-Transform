import sys, os, json

def findHTID(record,problems):
	for field in record['fields']:
		if '974' in field:
			for subfield in field['974']['subfields']:
				if 'u' in subfield:
					if subfield['u'] in problems:
						print(subfield['u'])
						return True

	return False

def main():
	problems = []
	with open('problematic-ids2.txt','r') as readfile:
		line = readfile.readline()
		while line:
			problems.append(line.strip())
			line = readfile.readline() 

	for root, dirs, files in os.walk('20190613'):
		for f in files:
			if f != '.DS_Store':
				with open(root + '/' + f,'r') as jsonl_file:
					lines = jsonl_file.readlines()
					for line in lines:
						record = json.loads(line)
						if findHTID(record,problems):
							print(f)

main()