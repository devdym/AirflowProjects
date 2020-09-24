import pandas as pd
import os


def read_wingAngle(file):
	"""
	Parses sts files from Nav with DigiBirds wing angles for single line

	Returns
	-------
	[Pandas DataFrame]
		wing angle data
	"""

	data = pd.read_csv(file, sep='\t', encoding='cp1252', skiprows=4)
	data.rename(columns={'Name': 'name', 'Min': 'min', 'Max': 'max', 'Mean': 'mean', 'SD': 'sd', '# Obs': 'obs',
						 '# Rej': 'rej'}, inplace=True)
	data['name'] = data['name'].str[:6]
	data['streamer'] = data['name'].str[1:3]
	data['streamer'] = data['streamer'].astype(int)
	data['compass'] = data['name'].str[-2:]
	data['compass'] = data['compass'].astype(int)
	f = os.path.basename(file)
	f = f.split('-')
	data['linename'] = f[0] + '-' + f[1]
	data['seq'] = data['linename'].str[-3:]
	data['seq'] = data['seq'].astype(int)

	return data
