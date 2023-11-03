Columns in the csv file:
unnamed,id,url,region,region_url,price,year,manufacturer,model,condition,cylinders,fuel,odometer,title_status,transmission,VIN,drive,size,type,paint_color,image_url,description,county,state,lat,long,posting_date,removal_date

```SQL
CREATE TABLE craigslist_vehicles (
	unnamed VARCHAR,
	id  VARCHAR PRIMARY KEY,
	url VARCHAR,
	region_url VARCHAR,
	price FLOAT,
	year DATE,
	manufacturer VARCHAR,
	model VARCHAR,
	condition VARCHAR,
	cylinders VARCHAR,
	fuel VARCHAR,
	odometer INT,
	title_status VARCHAR,
	transmission VARCHAR,
	VIN VARCHAR,
	drive VARCHAR,
	size VARCHAR,
	type VARCHAR,
	paint_color VARCHAR,
	image_url VARCHAR,
	description TEXT,
	county VARCHAR,
	state VARCHAR,
	lat FLOAT,
	long FLOAT,
	posting_date DATE,
	removal_date DATE
)
```
Convert .csv file to .tsv to circumvent issues with varied number of commas in each line due to textual information with commas

```Python
import csv

with open("craigslist_vehicles.csv", 'r') as input_file, open("craigslist_vehicles.tsv", 'w') as output_file:
  csv_reader = csv.reader(input_file)
  tsv_writer = csv.writer(output_file, delimiter='\t')

  for row in csv_reader:
     tsv_writer.writerow(row)
```


move the CSV to /tmp/ folder avoid permission issues given that we are using a different user ("postgress") who is different from the normal user ("derrick_mbarani") who is the owner of the file.

```SQL
COPY your_table_name FROM '/path/to/your/file.tsv' WITH (FORMAT csv, DELIMITER E'\t', HEADER);
```