import pandas as pd
import os
from datetime import datetime
from sqlalchemy import create_engine

def read_battery_short(file):
	"""
	Parse DigiCOURCE battery stats from text file

	Returns
	-------
	[Pandas DataFrame]
		battery stats data
	"""

	batt = []

	with open(file) as fp:
		line = fp.readline()
		cnt = 1
		while line:
			if len(line) == 22:
				# print("Line {}: {}".format(cnt, line.strip()))
				tmp = line.strip().split(' ')
				while ('' in tmp):
					tmp.remove('')
				batt.append(tmp)
			# tmp.clear()
			line = fp.readline()
			cnt += 1

	df = pd.DataFrame(batt, columns=['unit', 'bankA', 'bankB', 'activeBank'])
	f = os.path.basename(file)
	f = f.split()
	da = f[2]
	datetime_object = datetime.strptime(da, '%m%d%y')
	df['bankA'] = df['bankA'].astype('float')
	df['bankB'] = df['bankB'].astype('float')
	df['streamerNumber'] = df['unit'].str.slice(1, 3)
	df['unitName'] = df['unit'].str.slice(3, 4)
	df['unitNumber'] = df['unit'].str.slice(4, 6)
	df['date_'] = datetime_object
	return df
