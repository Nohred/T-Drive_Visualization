import pandas as pd
import os
import glob
from typing import Optional, Dict, Any

def read_taxi_logs(
    directory: str = "data/taxi_log_2008_by_id", 
    n_files: Optional[int] = None,
    read_csv_kwargs: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Read taxi log files from the specified directory and combine them into a single DataFrame.
    
    Args:
        directory (str): Path to the directory containing taxi log files
        n_files (Optional[int]): Number of files to read. If None, read all files.
        read_csv_kwargs (Optional[Dict]): Additional parameters to pass to pd.read_csv
        
    Returns:
        pd.DataFrame: Combined DataFrame with data from all files
    """
    # Default parameters for reading CSV
    csv_params = {
        'delimiter': ',',
        'header': None,
    }
    
    # Update with user-provided parameters
    if read_csv_kwargs:
        csv_params.update(read_csv_kwargs)
    
    # Get list of all txt files in the directory
    file_pattern = os.path.join(directory, "*.txt")
    all_files = sorted(glob.glob(file_pattern))
    
    if not all_files:
        raise FileNotFoundError(f"No .txt files found in directory: {directory}")
    
    # Limit to first n_files if specified
    if n_files is not None:
        all_files = all_files[:n_files]
    
    print(f"Reading {len(all_files)} taxi log files...")
    
    # Read and combine all files
    dfs = []
    for i, file_path in enumerate(all_files):
        try:
            df = pd.read_csv(file_path, **csv_params)
            
            dfs.append(df)
            
            # Print progress for large numbers of files
            if (i+1) % 100 == 0 or i+1 == len(all_files):
                print(f"Processed {i+1}/{len(all_files)} files...")
                
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    
    if not dfs:
        raise ValueError("No data could be read from the files")
    
    # Combine all DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)
    
    print(f"Successfully created DataFrame with {len(combined_df)} records")
    
    return combined_df

# Example usage
if __name__ == "__main__":
    try:
        # For customizing how files are read
        csv_options = {
            'delimiter': ',',
            'header': None,
            'names': ['id','timestamp' ,'latitude', 'longitude']  # Example column names
        }
        
        # Read all files
        # all_data = read_taxi_logs(read_csv_kwargs=csv_options)
        # print(f"Total records: {len(all_data)}")
        # print(f"Sample of data:\n{all_data.head()}")
        
        # Read only first 5 files
        sample_data = read_taxi_logs(n_files=5, read_csv_kwargs=csv_options)
        print(f"Sample records: {len(sample_data)}")
        print(f"Sample of data:\n{sample_data.head()}")
        print(f"Data info:\n{sample_data.info()}")
        
    except Exception as e:
        print(f"An error occurred: {e}")