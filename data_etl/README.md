![powerBI screenshot](https://github.com/Sciederrick/dbt_craigslist_vehicles/blob/main/screenshot.png)

### Extract Transform Load & Visualize Craigslist Vehicles Data

*Featuring PostgreSQL, Snowflake, DBT & PowerBi*

This README documents ETL process in data engineering using modern data tools.

### Data Source

**Source File**
Columns in the csv file:
unnamed,id,url,region,region_url,price,year,manufacturer,model,condition,cylinders,fuel,odometer,title_status,transmission,VIN,drive,size,type,paint_color,image_url,description,county,state,lat,long,posting_date,removal_date

**Derived SQL Schema**
<a name="SQL_schema"></a>

```SQL
CREATE TABLE craigslist_vehicles (
	"unnamed" VARCHAR,
	"id"  VARCHAR PRIMARY KEY,
	"url" VARCHAR,
	"region" VARCHAR,
	"region_url" VARCHAR,
	"price" FLOAT,
	"year" DATE,
	"manufacturer" VARCHAR,
	"model" VARCHAR,
	"condition" VARCHAR,
	"cylinders" VARCHAR,
	"fuel" VARCHAR,
	"odometer" INT,
	"title_status" VARCHAR,
	"transmission" VARCHAR,
	"vin" VARCHAR,
	"drive" VARCHAR,
	"size" VARCHAR,
	"type" VARCHAR,
	"paint_color" VARCHAR,
	"image_url" VARCHAR,
	"description" TEXT,
	"state" VARCHAR,
	"lat" FLOAT,
	"long" FLOAT,
	"posting_date" DATE,
	"removal_date" DATE
)
```

### Data Cleaning

* Do away with empty `county` column as it doesnot have any value for all rows
* Impute null/missing values with mean and mode
* Generate a clean csv file based on the aforementioned procedures

[Script file](./clean_csv.py) to run on the command line for data cleaning.

```Python
import argparse
import os
import pandas as pd
from tqdm import tqdm

parser = argparse.ArgumentParser(prog='csv to tsv', description='a script that converts csv to tsv line by line')
parser.add_argument('--input_file_path', required=True, type=str, help='path to .csv file')
args = parser.parse_args()

def impute_missing_values(df):
# Don't impute VIN, lat, long, image_url, removal_date values
    mean_value = df['odometer'].mean()

    df['odometer'].fillna(int(mean_value), inplace=True)

    categorical_columns = ['year', 'manufacturer', 'model', 'condition', 'cylinders', 'fuel', 'title_status',
                           'transmission', 'drive', 'size', 'type', 'paint_color', 'posting_date']

    df[categorical_columns] = df[categorical_columns].apply(lambda x: x.fillna(x.mode().iloc[0]))

    return df

def convert_to_appropriate_types(df):
    df = df.convert_dtypes() # convert to best possible types
    df['price'] = df['price'].apply(float)
    df['year'] = pd.to_datetime(df['year'], format='%Y')
    df['posting_date'] = pd.to_datetime(df['posting_date'], utc=True)
    df['removal_date'] = pd.to_datetime(df['removal_date'], utc=True)

    return df

def main():
    try:
        df = pd.read_csv(args.input_file_path, engine='python', on_bad_lines='warn')

        df = convert_to_appropriate_types(df)

        # drop county, all rows are missing
        df = df.drop(columns=['county'])

        df = impute_missing_values(df)

        destination_dir = os.path.dirname(args.input_file_path)
        file_name = os.path.basename(args.input_file_path)
        df.to_csv(destination_dir + '/' + file_name.split('.')[0] + '_cleaned.csv', index=False)
    except FileNotFoundError:
        print('input file not found')
    except BaseException:
        print('something went wrong')
    else:
        print("cleaning complete, filename {}".format(args.input_file_path))

if __name__ == '__main__':
    main()
```

### Loading the clean csv file data on postgreSQL

* Move the CSV to /tmp/ folder avoid permission issues given that we are using a different user ("postgress") who is different from the normal user ("derrick_mbarani") who is the owner of the file.

* Use sed to remove the first row containing column definitions before storing the data in postgress

```Shell
sed -n '1d' '/tmp/craigslist_vehicles_cleaned.csv'
```

* Ensure the order of the table schema columns is exactly the same as that in the .csv file, also ensure the datatypes are compatible

```SQL
COPY craigslist_vehicles FROM '/tmp/craigslist_vehicles_cleaned.csv' DELIMITER ',' CSV HEADER;
```

Use as a suffix replacing the above code snippet with the SQL command placeholder if not yet logged into the psql shell
`psql -d your_database_name -U your_user_name -c <SQL command>`

### Moving the data to Snowflake

* Export table data as .csv
```SQL
COPY craigslist_vehicles TO '/tmp/craigslist_vehicles_clean.csv' DELIMITER ',' CSV HEADER;
```

* Split the .csv data before loading to Snowflake

```shell
split -l 10000 --additional-suffix .csv './craigslist_vehicles_clean.csv' chunk_
```
Each .csv file will have the prefix `chunk`

* Load these files from the Snowflakes web interface

![Snowflake dashboard image showing manual data](./../screenshots/Screenshot%202023-11-09%20171459.png)
To load the data on Snowflake:
* Create account
* Create Database
* Use the default `public` schema (a schema is a logical goruping of related database objects)
* Create a table [SQL statement](#SQL_schema)
* Load data using the web interface file picker (select all relevant files at once)

### Transforming data with DBT (Database Tool)

Relevant link: [Github Repository](https://github.com/Sciederrick/dbt_craigslist_vehicles)


