import csv
import os

INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'


def read_data(file_name, delimiter=','):
	data = []

	with open(file_name, 'r') as f:
		reader = csv.reader(f, delimiter=delimiter)
		for row in reader:
			data.append(row)

	return data


def process_data(data):
	print(data)
	return data


def write_output(file_name, data):
	pass


def main():
	if not os.path.exists(OUTPUT_FOLDER):
		os.makedirs(OUTPUT_FOLDER)

	for file_name in os.listdir(INPUT_FOLDER):
		name, ext = os.path.splitext(file_name)

		delimiter = ','
		if ext == '.tsv':
			delimiter = '\t'

		data = read_data(os.path.join(INPUT_FOLDER, file_name), delimiter)
		result = process_data(data)
		write_output(os.path.join(OUTPUT_FOLDER, name + '.out'), result)


if __name__ == '__main__':
	main()
