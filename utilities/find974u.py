import sys, os, json

def find974u(record,records):
	for field in record['fields']:
		if '974' in field:
			for subfield in field['974']['subfields']:
				if 'u' in subfield:
					if subfield['u'] in records:
						print(subfield['u'])

	return False

def main():
	records = set(['uc1.31822011397684','uva.x030444573','mdp.49015000988593','osu.32435003322955','mdp.49015002156876'])
	print(records)

	for root, dirs, files in os.walk('20190613'):
		for f in files:
			if f != '.DS_Store':
				with open('20190613/' + f,'r') as jsonl_file:
					lines = jsonl_file.readlines()
					for line in lines:
						record = json.loads(line)
						find974u(record,records)

main()