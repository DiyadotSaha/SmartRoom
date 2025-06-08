import zipfile
import os
import pandas as pd

def unzip_and_process(datafile_paths):
    """
    Unzips data files from the provided paths and processes the contents.
    
    :param datafile_paths: List of file paths to the zip files
    :return: None
    """
    
    for file_path in datafile_paths:
        # Check if it's a valid zip file
        if zipfile.is_zipfile(file_path):
            # Get the directory where the zip file is located
            extract_dir = os.path.splitext(file_path)[0]  # Extracting the directory path without extension
            if not os.path.exists(extract_dir):
                os.makedirs(extract_dir)
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                print(f"Unzipping {file_path} to {extract_dir}...")
                zip_ref.extractall(extract_dir)
        else:
            print(f"{file_path} is not a valid zip file!")
    
    # Process the extracted files
    #process_unzipped_files(extract_dir)

def dataset1_processing(parent_dir):
    """
    Combines all CSVs in each subfolder of the given directory into one CSV per folder,
    ensuring the final CSV has the columns: co2, humidity, light, pir, temperature.
    
    :param parent_dir: Directory containing subfolders with CSV files
    :return: None
    """
    # Loop through all subdirectories in the parent directory
    for subdir, _, files in os.walk(parent_dir):
        # Ensure the directory is not the root directory and that we have exactly 5 files
        folder_name = os.path.basename(subdir)
        if len(files) == 5:
            # List of CSV filenames we expect to find
            expected_files = ['co2.csv', 'humidity.csv', 'light.csv', 'pir.csv', 'temperature.csv']

            # Initialize a list to hold the dataframes
            dfs = []

            # Loop through the expected CSV files and read them
            for expected_file in expected_files:
                file_path = os.path.join(subdir, expected_file)
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    # Ensure only the first column is kept
                    if df.shape[1] > 1:
                        df = df.iloc[:, 0]  # Selecting only the first column if extra columns exist
                    dfs.append(df)
                else:
                    print(f"Missing {expected_file} in {subdir}, skipping this folder.")
                    break
            else:
                # Concatenate all the dataframes side by side (horizontally)
                combined_df = pd.concat(dfs, axis=1)

                # Rename the columns to match the desired names
                combined_df.columns = ['co2', 'humidity', 'light', 'pir', 'temperature']

                # Save the combined DataFrame as a CSV with the folder name
                output_file = os.path.join(parent_dir, f"{folder_name}.csv")
                combined_df.to_csv(output_file, index=False)
                
        else:
            print(f"Skipping folder {subdir} as it does not contain exactly 5 CSV files.")



def dataset4_processing(input_folder):
    """
    Converts all valid .txt files in the input folder to .csv files in a new folder 
    named '{input_folder}_cleaned'. Each line in the .txt file must have exactly 
    3 comma-separated values: [timestamp, relative_humidity, temperature].

    Parameters:
        input_folder (str): Path to the folder containing .txt files.
    """

    # Create cleaned output directory
    output_folder = input_folder.rstrip('/\\') + "_cleaned"
    os.makedirs(output_folder, exist_ok=True)

    def is_valid_file(filepath):
        try:
            with open(filepath, 'r') as f:
                for i, line in enumerate(f):
                    if not line.strip():
                        continue
                    parts = line.strip().split(',')
                    if len(parts) != 3:
                        return False
                    if i >= 10:
                        break
            return True
        except Exception as e:
            print(f"Error checking {filepath}: {e}")
            return False

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            txt_path = os.path.join(input_folder, filename)
            
            if is_valid_file(txt_path):
                try:
                    df = pd.read_csv(txt_path, header=None, names=["time", "relative_humidity", "temperature"])
                    base_name = os.path.splitext(filename)[0]
                    csv_path = os.path.join(output_folder, base_name + ".csv")
                    df.to_csv(csv_path, index=False)
                    print(f"Converted {filename} -> {csv_path}")
                except Exception as e:
                    print(f"Failed to convert {filename}: {e}")
            else:
                print(f"Skipped {filename} (invalid format)")

    
# Example usage:
# change the file paths to 
datafile_paths = [
    '/Users/diya/SmartRoom/dataset_1/archive.zip', 
    '/Users/diya/SmartRoom/dataset_2/6_datasets.zip', 
    '/Users/diya/SmartRoom/dataset_3/smart-homes-temperature-time-series-forecasting.zip', 
    '/Users/diya/SmartRoom/dataset_4/dxyvxk6h96-2.zip'
    ]

#unzip_and_process(datafile_paths)
# add dir path to folder inside dataset 1 KEITH
#dataset1_processing('/Users/diya/SmartRoom/dataset_1/archive/KETI')
# add dir path to folder inside dataset 4 October
dataset4_processing('/Users/diya/SmartRoom/dataset_4/dxyvxk6h96-2/dxyvxk6h96-2/October')
# add dir path to folder inside dataset 4 October
dataset4_processing('/Users/diya/SmartRoom/dataset_4/dxyvxk6h96-2/dxyvxk6h96-2/November')

