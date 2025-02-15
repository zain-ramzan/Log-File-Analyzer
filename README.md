# Log File Analyzer

## Overview
The Log File Analyzer is a tool designed to analyze log files generated during 3D manufacturing projections. It provides insights into various parameters such as projection time, duration, date, and temperature variations. Users can upload multiple log files for analysis, and the application presents the results in an intuitive graphical format.

## Features
- **Graphical Representation**: Visualizes data including projection duration, start and end times, and temperature trends.
- **Multiple File Upload**: Supports analysis of multiple log files simultaneously.
- **Statistical Insights**: Provides minimum and maximum temperature values recorded during the process.
- **User-Friendly Interface**: Easy navigation and data interpretation for researchers and engineers.
  
## What we do
- **Temperature**: For Temperature, extracted *plcToPc-elevatorTemp* column values
- **Time**: For Time, extracted and convert *System time* to uniform Time as it is in Unix code.
   
## How to Use
1. **Application**: Run the application, and upload the logfiles which are provided
2. **Upload Log Files**: Select one or more log files for analysis.
3. **View Data Insights**: The system will process and display key information such as projection time, duration, and temperature trends.
4. **Analyze Graphs**: Study the graphical representation for deeper insights into manufacturing conditions.
5. **Export Data**: If required, export processed data for further use.

## System Requirements
- Python 3.x
- Required Libraries:
  - Pandas
  - Matplotlib
  - NumPy
  - Flask (if using a web-based version)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/zain-ramzan/Log-File-Analyzer.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Log File Analyzer
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Contribution Guide
Future students can extend the project by:
- Improving visualization with interactive graphs.
- Adding support for additional log file formats.
- Implementing real-time log monitoring.
- Enhancing the UI for better usability.

## Contact
For further queries, please reach out to me on <a href="www.linkedin.com/in/zainramzan" target="_blank">LinkedIn</a>

