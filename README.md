Certainly! Below is a comprehensive `README.md` file tailored for your **Photo and Video Organizer** project. This documentation will help you and others understand the purpose, setup, usage, and structure of the project.

---

# Photo and Video Organizer

A Python-based program to organize your photos and videos locally by extracting metadata, handling duplicates, and structuring files into organized directories.

## Features

- **Metadata Extraction**: Extracts timestamps and GPS data from images and videos.
- **Geolocation Mapping**: Converts GPS coordinates into human-readable location names.
- **Duplicate Detection and Cleanup**: Identifies and moves duplicate files to a designated trash directory.
- **File Renaming and Organization**: Renames files based on timestamp and location, organizing them into year/month folders.
- **Video Handling**: Processes video files similarly to images.
- **Logging**: Keeps detailed logs of all operations for tracking and troubleshooting.

## Project Structure

```plaintext
/PhotoOrganizer/
├── main.py                          # Entry point of the program
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
├── /logs/                           # Log files
│   └── photo_organizer.log
├── /input_media/                    # Directory containing original media files
│   ├── IMG_001.jpg
│   ├── VID_001.mp4
│   └── ...
├── /output_media/                   # Directory for organized media
│   ├── 2024/
│   │   ├── 2024-10/
│   │   │   ├── 20241014_Huntington_Beach.jpg
│   │   │   └── ...
│   │   └── ...
│   └── ...
├── /trash_duplicates/               # Directory for duplicate files
│   ├── IMG_001_DUPLICATE.jpg
│   └── ...
├── /modules/                        # Directory for individual modules
│   ├── __init__.py                  # Makes 'modules' a Python package
│   ├── metadata_extractor.py        # Module for metadata extraction
│   ├── geolocation_mapper.py        # Module for reverse geocoding
│   ├── duplicate_detector.py        # Module for duplicate detection
│   ├── file_organizer.py            # Module for renaming and organizing files
│   ├── video_handler.py             # Module for handling videos
│   ├── logger.py                    # Module for logging
│   └── utils.py                     # Utility functions
└── /known_faces/                    # Directory for storing known face encodings
    ├── known_faces.dat               # Serialized known face encodings and names
    └── ...
```

## Setup Instructions

### Prerequisites

- **Operating System**: Windows 11
- **Python Version**: 3.7 or higher
- **Python Libraries**: Listed in `requirements.txt`

### Installation

1. **Clone the Repository**

   Open Command Prompt or PowerShell and run:

   ```bash
   git clone https://github.com/YourUsername/PhotoOrganizer.git
   cd PhotoOrganizer
   ```

2. **Install Dependencies**

   Ensure you have Python 3.7+ installed. Then, install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install MediaInfo**

   The `pymediainfo` library requires the MediaInfo tool.

   - **Download MediaInfo** from the [official website](https://mediaarea.net/en/MediaInfo/Download/Windows).
   - Install it and ensure it's added to your system's PATH.

4. **Prepare Directories**

   - **Input Directory**: Place all your photos and videos in the `input_media/` folder.
   - **Output Directory**: Ensure the `output_media/` folder exists; the program will organize files here.
   - **Trash Directory**: The `trash_duplicates/` folder will store duplicate files.

### Running the Program

1. **Open Command Prompt or PowerShell**

2. **Navigate to the Project Directory**

   ```bash
   cd C:\Users\Quentin\Documents\GitHub\photo-and-video-Organizer
   ```

3. **Execute the Program**

   Run the script with the specified input and output directories:

   ```bash
   python main.py --input_dir "C:\\Users\\Quentin\\Downloads\\iCloud Photos" --output_dir "C:\\Users\\Quentin\\Pictures" --trash_dir "C:\\Users\\Quentin\\Pictures\\trash_duplicates"
   ```

   **Parameters:**

   - `--input_dir`: Path to the directory containing your original media files.
   - `--output_dir`: Path to the directory where organized media will be stored.
   - `--trash_dir`: Path to the directory where duplicate files will be moved.

   **Example:**

   ```bash
   python main.py --input_dir "C:\\Users\\Quentin\\Downloads\\iCloud Photos" --output_dir "C:\\Users\\Quentin\\Pictures" --trash_dir "C:\\Users\\Quentin\\Pictures\\trash_duplicates"
   ```

### Logs

All operations are logged in the `logs/photo_organizer.log` file. You can review this file to see details about processed files, duplicates moved, and any errors encountered.

## Testing

Before running the program on your entire media collection, it's recommended to test it with a small subset of files to ensure everything works as expected.

1. **Create a Test Input Directory**

   Copy a few media files to a separate folder within `input_media/`.

2. **Run the Program**

   Execute the script as described above.

3. **Verify the Results**

   - Check the `output_media/` folder to ensure files are correctly renamed and organized.
   - Check the `trash_duplicates/` folder for any duplicates.
   - Review the `logs/photo_organizer.log` file for detailed information.

## Troubleshooting

### Common Issues

1. **TypeError: 'IFDRational' object is not subscriptable**

   - **Cause**: This occurs when the program attempts to access GPS data in an unsupported format.
   - **Solution**: Ensure the `get_decimal_from_dms` function in `geolocation_mapper.py` correctly handles `IFDRational` objects by accessing their `.num` and `.den` attributes.

2. **MediaInfo Not Found**

   - **Cause**: `pymediainfo` requires the MediaInfo tool to be installed and accessible via PATH.
   - **Solution**: Verify that MediaInfo is installed and added to your system's PATH. You can test this by running `mediainfo` in Command Prompt.

3. **Permission Errors**

   - **Cause**: The script may not have the necessary permissions to read from the input directory or write to the output/trash directories.
   - **Solution**: Run Command Prompt or PowerShell as an administrator or adjust folder permissions accordingly.

### Debugging Tips

- **Check Logs**: The `photo_organizer.log` file contains detailed information about each operation and any errors encountered.
- **Run in Debug Mode**: Modify the logging level in `logger.py` to `DEBUG` for more verbose output.

  ```python
  logging.basicConfig(
      filename=log_file_path,
      filemode='a',
      format='%(asctime)s - %(levelname)s - %(message)s',
      level=logging.DEBUG  # Changed from INFO to DEBUG
  )
  ```

- **Test with a Single File**: Start by processing a single media file to ensure that metadata extraction and file organization work correctly.

## Future Enhancements

- **Facial Recognition and Learning**
- **Automatic Tagging for Enhanced Searchability**
- **Advanced Duplicate Detection (e.g., perceptual hashing)**
- **GUI Interface for Easier Interaction**
- **Support for RAW Image Files**
- **Custom Configuration Files for User Preferences**

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or feature additions.

## License

[MIT License](LICENSE)

## Contact

For any questions or support, please contact [Quentin](mailto:quentin@example.com).

---

Feel free to customize this `README.md` further to fit any additional specifics or preferences you might have. Let me know if you need any more assistance!