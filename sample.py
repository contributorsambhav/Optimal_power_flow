import csv

def csv_to_matrix(file_path):
    matrix = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Read the header
        matrix.append(header)
        for row in reader:
            if "Age" in header:  # Ensure there is an Age column
                age_index = header.index("Age")
                row[age_index] = str(int(row[age_index]) + 5) if row[age_index].isdigit() else row[age_index]
            matrix.append(row)
    return matrix

def save_matrix_to_file(matrix, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(matrix)

if __name__ == "__main__":
    file_path = "sample.csv"  # Replace with your CSV file path
    output_file = "output.csv"  # File to store the output matrix
    result = csv_to_matrix(file_path)
    save_matrix_to_file(result, output_file)
    print(f"Matrix saved to {output_file}")