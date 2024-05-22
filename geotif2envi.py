import argparse
from osgeo import gdal
import os
from datetime import datetime
import re

"""
This script is used to convert GeoTIFF files to ENVI format, generate an output file list, and a time vector.

Author: Zhanzhang Cai
Email: zhanzhang.cai@nateko.lu.se

Usage:
    python geotif_to_envi.py path_to_file_list.txt path_to_output_folder [--output_dtype uint8|int16|float32]

Arguments:
    path_to_file_list.txt  : Path to the text file containing the list of GeoTIFF files.
    path_to_output_folder  : Path to the output folder where the ENVI files and output lists will be saved.
    --output_dtype         : (Optional) Data type for the output ENVI files. Choices are 'uint8', 'int16', and 'float32'. Default is 'float32'.

Example:
    python geotif_to_envi.py filelist_input.txt ./output --output_dtype int16

Generating Input File List:
    You can generate the input file list using the following command:
    1. open Terminal (Linux/MacOS)
    2. type: ls -d $PWD/*.tif > filelist_input.txt
"""

def extract_date_from_filename(filename, date_format):
    # Extract the date string based on the provided format
    match = re.search(date_format, filename)
    if match is None:
        raise ValueError(f"Date format not found in filename: {filename}")
    date_str = match.group()
    # Convert the date string to datetime object
    date_obj = datetime.strptime(date_str, '%Y%m%d')
    # Convert to YYYYDOY format
    doy = date_obj.timetuple().tm_yday
    return f"{date_obj.year}{doy:03d}"

def geotiff_to_envi(file_list, output_folder, output_dtype, date_format):
    dtype_map = {
        'float32': gdal.GDT_Float32,
        'int16': gdal.GDT_Int16,
        'uint8': gdal.GDT_Byte
    }

    if output_dtype not in dtype_map:
        raise ValueError(f"Unsupported data type: {output_dtype}. Supported types are: {list(dtype_map.keys())}")

    output_files = []
    time_vector = []

    for geotiff_path in file_list:
        # Extract date from the filename
        date_str = extract_date_from_filename(os.path.basename(geotiff_path), date_format)
        time_vector.append(date_str)

        # Generate output file path
        output_filename = os.path.splitext(os.path.basename(geotiff_path))[0] + '.img'
        output_path = os.path.join(output_folder, output_filename)
        output_files.append(output_path)

        # Open the GeoTIFF file
        src_ds = gdal.Open(geotiff_path, gdal.GA_ReadOnly)
        if src_ds is None:
            raise FileNotFoundError(f"Unable to open GeoTIFF file: {geotiff_path}")

        # Get metadata from source dataset
        width = src_ds.RasterXSize
        height = src_ds.RasterYSize
        bands = src_ds.RasterCount
        geotransform = src_ds.GetGeoTransform()
        projection = src_ds.GetProjection()

        # Create ENVI driver
        driver = gdal.GetDriverByName('ENVI')
        if driver is None:
            raise RuntimeError("ENVI driver not available")

        # Create the ENVI output file with specified data type
        dst_ds = driver.Create(output_path, width, height, bands, dtype_map[output_dtype])
        if dst_ds is None:
            raise RuntimeError(f"Unable to create ENVI file: {output_path}")

        # Set geotransform and projection
        dst_ds.SetGeoTransform(geotransform)
        dst_ds.SetProjection(projection)

        # Copy data from source to destination
        for band in range(1, bands + 1):
            src_band = src_ds.GetRasterBand(band)
            dst_band = dst_ds.GetRasterBand(band)
            data = src_band.ReadAsArray()
            dst_band.WriteArray(data)

        # Properly close the datasets
        src_ds = None
        dst_ds = None

    return output_files, time_vector

def read_file_list(file_path):
    with open(file_path, 'r') as file:
        file_list = file.read().splitlines()
    return file_list

def save_list_to_file(data_list, file_path):
    with open(file_path, 'w') as file:
        for item in data_list:
            file.write(f"{item}\n")

def main():
    parser = argparse.ArgumentParser(description="GeoTIFF to ENVI Conversion Tool")
    parser.add_argument("file_list_path", help="Path to the text file containing the list of GeoTIFF files")
    parser.add_argument("output_folder", help="Path to the output folder")
    parser.add_argument("--output_dtype", choices=['uint8', 'int16', 'float32'], default='float32',
                        help="Data type for the output ENVI files (default: float32)")
    args = parser.parse_args()

    file_list_path = args.file_list_path
    output_folder = args.output_folder
    output_dtype = args.output_dtype
    date_format = r'\d{8}'  # Assuming the date format is YYYYMMDD in the file names

    # Read the file list from the text file
    try:
        file_list = read_file_list(file_list_path)
    except FileNotFoundError:
        print(f"Error: The file list at {file_list_path} was not found. Exiting.")
        return

    # Convert GeoTIFF files to ENVI format
    try:
        output_files, time_vector = geotiff_to_envi(file_list, output_folder, output_dtype, date_format)
    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        return

    # Save output file list and time vector to text files in the output folder
    output_file_list_path = os.path.join(output_folder, 'ENVI_file_list.txt')
    time_vector_path = os.path.join(output_folder, 'time_vector.txt')

    save_list_to_file(output_files, output_file_list_path)
    save_list_to_file(time_vector, time_vector_path)

    print("Output Files saved to:", output_file_list_path)
    print("Time Vector saved to:", time_vector_path)

if __name__ == "__main__":
    main()
