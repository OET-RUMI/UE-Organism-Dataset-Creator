import csv
import os
import json

INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'
DIVERSITY_FILE = "diversity.csv"

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


def format_diversity_data(diversity_data):
	formatted_diversity_data = {}

	for row in diversity_data:
		aphia_id = row['WoRMS AphiaID']
		common_name = row['Common Name']
		scientific_name = row['Scientific Name']
		kingdom = row['Kindom']
		phylum = row['Phylum']
		class_name = row['Class']
		order = row['Order']
		family = row['Family']
		genus = row['Genus']
		species = row['Species']
		max_depth = row['Max Depth']
		min_depth = row['Min Depth']

		image = row['Link to Pic 1']
		if image == 'NA' or (not image.endswith('.png') and not image.endswith('.jpg')):
			image = row['Link to Pic 2']
		if image == 'NA' or (not image.endswith('.png') and not image.endswith('.jpg')):
			image = None

		formatted_diversity_data[aphia_id] = {
			'Common Name': common_name,
			'CombinedNameID': scientific_name,
			'Kingdom': kingdom,
			'Phylum': phylum,
			'Class': class_name,
			'Order': order,
			'Family': family,
			'Genus': genus,
			'Species': species,
			'Max Depth': max_depth,
			'Min Depth': min_depth,
			'Image': image
		}

	return formatted_diversity_data


def process_data(data, diversity_data={}):
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

		if row['AphiaID'] in diversity_data:
			row['VernacularName'] = diversity_data[row['AphiaID']]['Common Name']
			row['CombinedNameID'] = diversity_data[row['AphiaID']]['CombinedNameID']
			row['Image'] = diversity_data[row['AphiaID']]['Image']
			row['Max Depth'] = diversity_data[row['AphiaID']]['Max Depth']
			row['Min Depth'] = diversity_data[row['AphiaID']]['Min Depth']

		taxon_data = ['Animalia']

		for rank in TAXON_RANKS:
			if row[rank] and row[rank] != 'NA':
				taxon_data.append(row[rank])
			else:
				break

		if not 'Image' in row:
			row['Image'] = ""

		if not 'Max Depth' in row or row['Max Depth'] == 'NA' or row['Max Depth'] == '':
			row['Max Depth'] = 0
		else:
			row['Max Depth'] = float(row['Max Depth'])
		
		if not 'Min Depth' in row or row['Min Depth'] == 'NA' or row['Min Depth'] == '':
			row['Min Depth'] = 0
		else:
			row['Min Depth'] = float(row['Min Depth'])

		organism_data = {
			'Name': row['AphiaID'],
			'Common Name': row['VernacularName'].title(),
			'Scientific Name': row['CombinedNameID'],
			'Taxonomy': {
				'Taxonomy Chain': taxon_data
			},
			'Highlight Image': row['Image'],
			'Max Depth': row['Max Depth'],
			'Min Depth': row['Min Depth']
		}

		organisms.append(organism_data)

	# get the rows of all spotting events
	i = 0
	spotting = []
	for row in data:
		if row['AphiaID'] == 'NA' or row['AphiaID'] == '-999':
			continue

		spotting_data = {
			'Name': str(i),
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

		i += 1

		spotting.append(spotting_data)

	return organisms, spotting


def write_json_data(file_name, data):
	json_data = json.dumps(data, indent=4)

	with open(file_name, 'w') as f:
		f.write(json_data)

def main():
	diversity_data = []
	if os.path.exists(DIVERSITY_FILE):
		diversity_data = read_data(DIVERSITY_FILE)
	
	diversity_data = format_diversity_data(diversity_data)

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
		organisms, spotting = process_data(overall_data, diversity_data)

		write_json_data(os.path.join(OUTPUT_FOLDER, name + "Organisms" + ".json"), organisms)
		write_json_data(os.path.join(OUTPUT_FOLDER, name + "Spotting" + ".json"), spotting)


if __name__ == '__main__':
	main()
