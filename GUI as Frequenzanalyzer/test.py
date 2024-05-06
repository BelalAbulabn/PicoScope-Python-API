import csv

def clean_csv(input_filename, output_filename):
    # Open the input CSV file for reading
    with open(input_filename, mode='r', encoding='utf-8') as infile:
        # Open the output CSV file for writing
        with open(output_filename, mode='w', newline='', encoding='utf-8') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            for row in reader:
                # Clean each cell in the row by removing '[' and ']'
                cleaned_row = [cell.replace('[', '').replace(']', '') for cell in row]
                # Write the cleaned row to the output file
                writer.writerow(cleaned_row)

# Example usage
input_filename = 'C:\\pico\\PicoScope-Python-API\\dut_values1220.csv'
output_filename = 'C:\\pico\\PicoScope-Python-API\\dut_values2220db.csv'

# input_filename = 'source.csv' # Replace with your source CSV file path
# output_filename = 'cleaned.csv' # The path for the output CSV file

clean_csv(input_filename, output_filename)
