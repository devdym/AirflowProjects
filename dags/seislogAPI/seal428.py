def read_linelog():
    """under construction

	Returns
	-------
	   none
	"""
def read_tension428(file):
	'''reads the csv file exported by Seal 408 with Streamer tension data'''
	d = ''
	s = 0

	with open(file) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=':')
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				d = row[1].strip()
			if line_count == 1:
				s = int(row[1].strip())
			if line_count >= 2:
				break
			line_count += 1

	data = pd.read_csv(file, sep='\t', skiprows=2)
	data.rename(columns={'    Time': 'time',
						 'Tension (daN)': 'tension',
						 'Head Buoy Power': 'hpower',
						 'Head Buoy Current (mA)': 'hcurrent',
						 'Output Voltage (V)': 'voltage'}, inplace=True)

	data['date_'] = d
	data['str'] = s
	data['date_'] = data['date_'] + ' ' + data['time']
	data['date_'] = data['date_'].astype('datetime64[ns]')
	data = data.drop('time', 1)

	return data
