# Genome Assembly Coordinate Converter

## Description
A web-based application that facilitates the conversion of genomic coordinates between human genome assemblies (hg37/GRCh37 to hg38/GRCh38 and vice versa). The tool also provides additional genomic annotations including gene information, variant details, and population frequencies.

## Developer
**Dr. Babajan Banaganapalli**  

## Features
- Convert genomic coordinates between hg37 and hg38 assemblies
- Single coordinate conversion with instant results
- Batch conversion support (CSV/TSV files)
- Additional genomic annotations:
  - Gene information
  - Known variants
  - Population frequencies (gnomAD)
- User-friendly interface with Bootstrap styling
- Detailed tabular results display

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup
1. Clone the repository

cd genome-coordinate-converter

python -m venv venv

3. Activate the virtual environment
- On Windows:
```bash
venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```

4. Install required packages
```bash
pip install -r requirements.txt
```

### Required Packages
Create a `requirements.txt` file with the following contents:
```
flask==2.0.1
pyliftover==0.4
pandas==1.3.0
requests==2.26.0
```

## Usage

### Running the Application
1. Start the Flask server:
```bash
python app.py
```

2. Open a web browser and navigate to:
```
http://localhost:5000
```

### Single Coordinate Conversion
1. Select conversion type (hg37→hg38 or hg38→hg37)
2. Enter chromosome (e.g., chr1)
3. Enter position
4. Click "Convert"

### Batch Conversion
1. Prepare a CSV/TSV file with columns:
   - chromosome
   - position
2. Select conversion type
3. Upload file
4. Results will download automatically

## Project Structure
```
genome-coordinate-converter/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
└── templates/
    └── index.html         # HTML template
```

## Technical Details
- **Framework**: Flask (Python)
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **APIs Used**:
  - Ensembl REST API
  - gnomAD API
- **Coordinate Conversion**: pyliftover package

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## Citation
If you use this tool in your research, please cite:
```
Banaganapalli, B. (2024). Genome Assembly Coordinate Converter. 
GitHub Repository: https://github.com/yourusername/genome-coordinate-converter
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
Dr. Babajan Banaganapalli  
Email: [Your Email]  
Institution: Department of Genetic Medicine,

## Acknowledgments
- UCSC Genome Browser
- Ensembl Project
- gnomAD Database

## Version History
- v1.0.0 (2024-01): Initial release
  - Basic coordinate conversion
  - Genomic annotations
  - Batch processing support
