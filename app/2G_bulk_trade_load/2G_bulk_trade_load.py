import pandas as pd
import os
import shutil
from datetime import datetime, date

# Function to move the file to the destination path
def move_and_delete_files(source_path, destination_path):
    try:
        shutil.move(source_path, destination_path)
    except Exception as e:
        print(f"Error moving file '{source_path}': {str(e)}")

# Delete the files in the original path
def delete_files_in_folder(folder_path):
    try:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)
            print(f"Deleted '{file_path}'.")
    except Exception as e:
        print(f"Error deleting files in folder '{folder_path}': {str(e)}")

# Get today's date in the format YYYYMMDDHHMM
today_date = datetime.today().strftime('%Y%m%d%H%M')

# Set the directory where the CSV files are located
source_directory = f'M:/Systems/Transactions'

# Specify the destination folder using today's date
input_destination_directory = f'M:/Systems/Transactions/{date.today().strftime("%Y-%m-%d")}-input'
combined_destination_directory = f'M:/Systems/Transactions/{date.today().strftime("%Y-%m-%d")}-combined'

# Create the destination folders if they don't exist
for directory in [input_destination_directory, combined_destination_directory]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Folder '{directory}' created.")

# Get a list of all CSV files in the source folder
csv_files = [file for file in os.listdir(source_directory) if file.endswith('.csv')]

# Check if there are any CSV files
if not csv_files:
    print("No CSV files found in the specified directory.")
else:
    # Initialize an empty list to store DataFrames
    dfs = []

    # Loop through each CSV file
    for idx, file in enumerate(csv_files):
        file_path = os.path.join(source_directory, file)

        # Read CSV file into a DataFrame, specifying the second column as string type to preserve leading zeros
        df = pd.read_csv(file_path, dtype={1: str})

        # Get today's date in the format M/DD/YYYY
        formatted_date = datetime.today().strftime('%m/%d/%Y').lstrip('0')
                
        # Change the name of the third header to today's date
        df.columns.values[2] = formatted_date

        # Remove rows containing the string 'TRAILER'
        df = df[~df.apply(lambda row: row.astype(str).str.contains('TRAILER').any(), axis=1)]

        # Replace 'Unnamed' strings in the header row with an empty string
        df.columns = [col if 'Unnamed' not in str(col) else '' for col in df.columns]

        if len(df.columns) > 18:
            # Change the value of 'External Transaction Code' (Column S) as something like YYYYMMDDHHMM001 for the first block
            df.iloc[:, 18] = today_date + str(idx + 1).zfill(3)

        # Ensure the DataFrame has at least 50 columns to include the AX column 
        while len(df.columns) < 50:
            df = pd.concat([df, pd.DataFrame(columns=[None])], axis=1)

        # Calculate the sum of the 'Quantity'(6th) column
        sum_6th_column = df.iloc[:, 5].sum()

        # Insert the sum to the AX(50th) column for each row
        df.insert(49, ' ', sum_6th_column)

        dfs.append(df)

        # Check if the input file has exactly one row
        if df.shape[0] == 1:
            # Empty the 18th and 50th columns' values if the block only has one transaction
            df.iloc[:, 18] = ''
            df.iloc[:, 49] = ''

    # Concatenate all DataFrames in the list into a single DataFrame
    combined_data = pd.concat(dfs, ignore_index=True)

    # Check if the combined DataFrame is not empty
    if not combined_data.empty:
        # Add a row at the end labeled as 'TRAILER' with the count of total transactions 
        row_count_value = combined_data.shape[0]
        combined_data.loc[len(combined_data.index)] = ['TRAILER', row_count_value] + [None] * (len(combined_data.columns) - 2)

        # Remove the last column
        combined_data = combined_data.iloc[:, :-1]

        # Save the combined DataFrame to a new CSV file
        output_file_path = os.path.join(combined_destination_directory, f'combined_output_{today_date}.csv')
        combined_data.to_csv(output_file_path, index=False)

        print(f"CSV files successfully combined, and saved as '{output_file_path}'.")
        
        # Move each CSV file to the input destination folder
        for file in csv_files:
            move_and_delete_files(os.path.join(source_directory, file), os.path.join(input_destination_directory, file))
        
        print("All CSV files moved.")
    else:
        print("Combined file not created. Files in the source folder will not be moved.")
