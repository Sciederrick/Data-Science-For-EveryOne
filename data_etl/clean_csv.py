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