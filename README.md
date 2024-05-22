# GeoTIFF to ENVI Conversion Tool

This repository contains a Python script for converting GeoTIFF files to ENVI format. It generates an output file list and a time vector for the converted files.

## Author

- **Zhanzhang Cai**
- **Email:** zhanzhang.cai@nateko.lu.se

## Description

This script is used to:
- Convert GeoTIFF files to ENVI format.
- Generate a file list of the converted ENVI files.
- Generate a time vector based on the date in the GeoTIFF filenames.

## Usage

### Command-Line Arguments

- `file_list_path` (str): Path to the text file containing the list of GeoTIFF files.
- `output_folder` (str): Path to the output folder where the ENVI files and output lists will be saved.
- `--output_dtype` (str, optional): Data type for the output ENVI files. Choices are `uint8`, `int16`, and `float32`. Default is `float32`.

### Example

```sh
python geotif_to_envi.py filelist_input.txt ./output --output_dtype int16

