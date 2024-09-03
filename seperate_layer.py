import json
import csv

def main():
    with open('') as file:
        data = json.load(file)

        for each in data['layers']:
            print(each['name'])
            layer_name = each['name']
            # print(each['data'])
            # Assuming you have a list of integers called 'int_list'
            # and you want to save it as a separate CSV file

            # Specify the file path for the CSV file
            csv_file_path = f'layers/{layer_name}.csv'

            # Open the CSV file in write mode
            with open(csv_file_path, 'w', newline='') as file:
                # Create a CSV writer object
                writer = csv.writer(file)

                # Write the list of integers to the CSV file
                writer.writerow(each['data'])
        # Process the JSON data here

if __name__ == "__main__":
    main()