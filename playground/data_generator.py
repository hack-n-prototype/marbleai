import csv
from faker import Faker

fake = Faker()

# Define the number of rows you want in the CSV file
num_rows = 1000000  # You can adjust this number based on your needs

# Define the fields in the CSV
fields = ['Name', 'Email', 'Phone', 'Address', 'date', 'country', 'job']

# Generate random data and write to CSV file
with open('data_person_2.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    # Write header
    csvwriter.writerow(fields)

    # Write rows with random data
    for _ in range(num_rows):
        row = [fake.name(), fake.email(), fake.phone_number(), fake.address(), fake.date(), fake.country(), fake.job()]
        csvwriter.writerow(row)

print(f"Sample data generated and saved to 'sample_data.csv'.")
