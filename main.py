import csv
import os
import json

INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'

TAXON_RANKS = ['Phylum', 'Class', 'Order', 'Family', 'Genus']


def date_time_to_timestamp(date, time):
	# date format: M/D/YYYY or MM/D/YYYY or M/DD/YYYY or MM/DD/YYYY
	# time format: HH:MM:SS
	# timestamp format: YYYY-MM-DDTHH:MM:SSZ

	# split date into month, day, year
	date_parts = date.split('/')
	month = date_parts[0].zfill(2)
	day = date_parts[1].zfill(2)
	year = date_parts[2]

	# split time into hour, minute, second
	time_parts = time.split(':')
	hour = time_parts[0]
	minute = time_parts[1]
	second = time_parts[2]

	# create timestamp
	timestamp = f"{year}-{month}-{day}T{hour}:{minute}:{second}Z"

	return timestamp


def read_data(file_name, delimiter=','):
	data = []

	with open(file_name, 'r') as f:
		# don't include header line in data
		header = f.readline().strip().split(delimiter)

		# process header line into list of headings
		headings = []
		for h in header:
			headings.append(h.strip())

		# store data by headings in a list of dictionaries
		reader = csv.reader(f, delimiter=delimiter)
		for row in reader:
			row_data = {}

			for i, value in enumerate(row):
				row_data[headings[i]] = value.strip()

			data.append(row_data)

	return data


def process_data(data):
	# get the rows of all unique organisms (basing uniqueness on the CombinedNameID)
	unique_organisms = []
	combined_name_set = set()

	for row in data:
		combined_name = row['CombinedNameID']
		if combined_name not in combined_name_set:
			combined_name_set.add(combined_name)
			unique_organisms.append(row)

	# get the rows of all unique organisms
	organisms = []
	for row in unique_organisms:
		if row['AphiaID'] == 'NA' or row['AphiaID'] == '-999':
			continue

		taxon_data = ['Animalia']

		for rank in TAXON_RANKS:
			if row[rank] and row[rank] != 'NA':
				taxon_data.append(row[rank])
			else:
				break

		organism_data = {
			'Name': row['AphiaID'],
			'Common Name': row['VernacularName'].title(),
			'Scientific Name': row['CombinedNameID'],
			'Taxonomy': {
				'Taxonomy Chain': taxon_data
			}
		}

		organisms.append(organism_data)

	# get the rows of all spotting events
	spotting = []
	for row in data:
		if row['AphiaID'] == 'NA' or row['AphiaID'] == '-999':
			continue

		spotting_data = {
			'Name': row['SampleID'],
			'AphiaID': row['AphiaID'],
			'Repository': row['Repository'],
			'Identified By': row['IdentifiedBy'],
			'Identification Date': row['IdentificationDate'],
			'Identification Qualifier': row['IdentificationQualifier'],
			'Identification Verification Status': row['IdentificationVerificationStatus'],
			'Latitude': float(row['Latitude']),
			'Longitude': float(row['Longitude']),
			'Depth': float(row['DepthInMeters']),
			'Observation Timestamp': date_time_to_timestamp(row['ObservationDate'], row['ObservationTime']),
			'Individual Count': int(row['IndividualCount']),
			'Condition': row['Condition'],
			'Observation Image': row['ImageFilePath']
		}

		spotting.append(spotting_data)

	return organisms, spotting


def write_json_data(file_name, data):
	json_data = json.dumps(data, indent=4)

	with open(file_name, 'w') as f:
		f.write(json_data)

def main():
	if not os.path.exists(OUTPUT_FOLDER):
		os.makedirs(OUTPUT_FOLDER)

	for file_name in os.listdir(INPUT_FOLDER):
		name, ext = os.path.splitext(file_name)

		delimiter = None
		if ext == '.csv':
			delimiter = ','
		elif ext == '.tsv':
			delimiter = '\t'

		if delimiter is None:
			continue

		overall_data = read_data(os.path.join(INPUT_FOLDER, file_name), delimiter)
		organisms, spotting = process_data(overall_data)

		write_json_data(os.path.join(OUTPUT_FOLDER, name + "Organisms" + ".json"), organisms)
		write_json_data(os.path.join(OUTPUT_FOLDER, name + "Spotting" + ".json"), spotting)


if __name__ == '__main__':
	main()
