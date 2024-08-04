import os
import pandas as pd

# Specify the directory you want to scan
#directory = 'F:\Segmentation_project\THP1_SN_20240703_221049\Test4_MF\Output'

# Create a list to store the results

def genmasterSheet(directory, savePath):

    results = []

    # Scan all files in the directory
    for filename in os.listdir(directory):
        # Check if the file is an Excel file
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            # Construct the full file path
            file_path = os.path.join(directory, filename)
            
            # Read the Excel file
            df = pd.read_excel(file_path)
            
            # Extract the last value in column A that contains a value
            last_value_in_A = df['Label'].dropna().iloc[-1]
            
            # Create a new DataFrame and append it to the list
            results.append(pd.DataFrame({'File Location': [file_path], 'Last Value in Column A': [last_value_in_A]}))

    # Concatenate all DataFrames in the list
    results = pd.concat(results, ignore_index=True)

    # Write the results to a new Excel file
    results.to_excel(savePath, index=False)
    print("Done summary file generation")
