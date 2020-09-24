import pandas as pd
import re
import csv
import sqlalchemy
from sqlalchemy import create_engine
from datetime import datetime
import os


def read_tension408(file):
	cntt = 0;
	data = []
	file_year = datetime.fromtimestamp(os.path.getctime(file)).strftime('%Y')
	with open(file, 'r', encoding='cp1252') as file1:
	    line = file1.readline()
	    while line:
	        if cntt > 18:
	            tmp = line.strip().split(' ')
	            while('' in tmp) :
	                tmp.remove('')
	            data.append(tmp)
	            cntt += 1
	        cntt += 1
	        line = file1.readline()

	df = pd.DataFrame(data)
	df =df.rename(columns={0:'streamer', 3:'tension', 5:'date_'})
	df['streamer'] = df['streamer'].str[1:].astype('int') # get str number
	df['tension'] = df['tension'].str[:-2].astype(int) # cut decimal 0
	df = df.drop(1, 1)
	df = df.drop(2, 1)
	df = df.drop(4, 1)
	df['date_'] = df['date_'].str[:3] # get julian day only
	df['date_'] = df['date_'] + file_year # add file creation year
	df['date_'] = pd.to_datetime(pd.Series(df['date_']), format="%j%Y") # parse to date

	m = df.groupby('streamer').tension.mean() # calc mean tension

	res = pd.DataFrame(m)
	res['date_'] = df['date_'][1] # add dat column
	res.reset_index(inplace=True)

	return res


def read_instest(file):
	'''reads the csv file exported by Seal 408 with Instrument tests data'''
	br_line = []

	with open(file, 'r', encoding='cp1252') as file1:
		line = file1.readline()
		cnt = 0
		while line:
			pattern = re.compile(r"(^-------------------------------------------------?)")
			cnt += 1
			if pattern.search(line) is not None:
				br_line.append(cnt)
			line = file1.readline()

	if 116 in br_line:
		start = br_line[7]
		end = br_line[8]
	else:
		start = br_line[4]
		end = br_line[5]

	data = []
	cntt = 0
	with open(file, 'r', encoding='cp1252') as file1:
		line = file1.readline()
		while line:
			if cntt > start - 1 and cntt < end - 1:
				tmp = line.strip().split(' ')
				while ('' in tmp):
					tmp.remove('')
				data.append(tmp)
			cntt += 1
			line = file1.readline()

	df = pd.DataFrame(data)
	df = df.drop(3, 1)
	df['updated'] = df[[10, 11, 12, 13]].apply(lambda x: ' '.join(x), axis=1)
	df = df.drop(10, 1)
	df = df.drop(11, 1)
	df = df.drop(12, 1)
	df = df.drop(13, 1)
	df.rename(columns={0: 'ass_sn', 1: 'trace', 2: 'streamer', 4: 'fdu_sn', 5: 'type', 6: 'cap', 7: 'cutoff',
					   8: 'noise', 9: 'leakage'}, inplace=True)  # rename columns
	df['updated'] = pd.to_datetime(df['updated'], format='%b %d, %Y %H:%M')
	df = df[df.cap != 'N/A']
	df['cap'].replace(regex=True,inplace=True,to_replace=r'\*', value=r'')
	df['cutoff'].replace(regex=True,inplace=True,to_replace=r'\*', value=r'')
	df['noise'].replace(regex=True,inplace=True,to_replace=r'\*', value=r'')
	df = df[df.noise != 'N/A']
	df['leakage'].replace(regex=True,inplace=True,to_replace=r'\*', value=r'')
	df['section_rank'] = None
	df['ch_nb'] = None
	df['failure'] = ''

	return df


def read_instest2(file):
	'''
	reads the csv file exported by Seal 408 with Instrument tests data
	'''
	start = 0
	data = []
	with open(file, 'r', encoding='cp1252') as file1:
		line = file1.readline()
		cnt = 0
		while line:
			if 'ALL SENSORS    Nb' in line:
				start =+ 1
			if start >= 1 and start <= 7:
				start += 1

			if start >= 7:
				if '--' in line:
					start = 0
				else:
					start += 1
					tmp = line.strip().split(' ')
					while ('' in tmp):
						tmp.remove('')
					data.append(tmp)
			line = file1.readline()

	df = pd.DataFrame(data)
	df = df.drop(3, 1)
	df['updated'] = df[[10, 11, 12, 13]].apply(lambda x: ' '.join(x), axis=1)
	df = df.drop(10, 1)
	df = df.drop(11, 1)
	df = df.drop(12, 1)
	df = df.drop(13, 1)
	df.rename(columns={0: 'ass_sn', 1: 'trace', 2: 'streamer', 4: 'fdu_sn', 5: 'type', 6: 'cap', 7: 'cutoff',
					   8: 'noise', 9: 'leakage'}, inplace=True)  # rename columns
	df['updated'] = pd.to_datetime(df['updated'], format='%b %d, %Y %H:%M')
	df = df[df.cap != 'N/A']
	df['cap'].replace(regex=True,inplace=True,to_replace=r'\*', value=r'')
	df['cutoff'].replace(regex=True,inplace=True,to_replace=r'\*', value=r'')
	df['noise'].replace(regex=True,inplace=True,to_replace=r'\*', value=r'')
	df = df[df.noise != 'N/A']
	df['leakage'].replace(regex=True,inplace=True,to_replace=r'\*', value=r'')
	df['section_rank'] = 0
	df['ch_nb'] = 0
	df['failure'] = ''

	return df


def read_instestlimits2(file, date):
	'''
	reads the csv file exported by Seal 408 with Instrument tests data
	'''

	with open(file, 'r', encoding='cp1252') as file1:
		line = file1.readline()
		cnt = 0
		read = True
		res = []
		while line:
			if 'ALL SENSORS' in line or not read:
				read = False
				if not read:
					tmp = line.strip().split(' ')
					while('' in tmp) :
						tmp.remove('')
						if "Noise" in tmp:
						    tmp.pop(0)
						if "Capacitance" in tmp:
						    tmp.pop(0)
						if "Leakage" in tmp:
						    tmp.pop(0)
						if "Cut" in tmp:
						    tmp.pop(0)
						if "Off" in tmp:
						    tmp.pop(0)

					res.append(tmp)
				if 'ALL SENSORS    Nb' in line:
					read = True
			line = file1.readline()

	res.pop(0)
	res.pop(0)
	res.pop(0)
	res.pop(0)
	res.pop(-1)
	res.pop(-1)

	dfl = pd.DataFrame(res)
	dfl[0] = dfl[0].str[1:2]
	dfl = dfl.drop(2, 1)
	dfl = dfl.drop(4, 1)

	sensorNb = int(round(len(dfl)/4))
	start = 0
	end = start + sensorNb

	noiseRes = dfl[start:end].copy()
	noiseRes = noiseRes.drop(3, 1)
	noiseRes.rename(columns={0: 'sensor_nb', 1: 'noise'}, inplace=True)
	start = start + sensorNb
	end = start + sensorNb

	capRes = dfl[start:end].copy()
	capRes.rename(columns={0: 'sensor_nb', 1: 'cap_min', 3: 'cap_max'}, inplace=True)
	start = start + sensorNb
	end = start + sensorNb

	leakageRes = dfl[start:end].copy()
	leakageRes = leakageRes.drop(3, 1)
	leakageRes.rename(columns={0: 'sensor_nb', 1: 'leakage'}, inplace=True)
	start = start + sensorNb
	end = start + sensorNb

	cutoffRes = dfl[start:end].copy()
	cutoffRes.rename(columns={0: 'sensor_nb', 1: 'cutoff_min', 3: 'cutoff_max'}, inplace=True)

	total = pd.merge(noiseRes, capRes, on=["sensor_nb"])
	total = pd.merge(total, cutoffRes, on=["sensor_nb"])
	total = pd.merge(total, leakageRes, on=["sensor_nb"])
	total['updated'] = date

	return total
