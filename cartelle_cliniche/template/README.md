# Clinical Folder Template

This folder contains a template structure for clinical data input.

## Structure:
- patient_info.json: Patient demographics and medical history
- notes/: Clinical notes and reports (.txt files)
- signals/: Signal data like ECG, EEG (.json or .csv files)
- images/: Medical images (.dcm, .png, .jpg files)

## Usage:
1. Update patient_info.json with actual patient data
2. Add clinical notes in notes/ folder
3. Add signal data in signals/ folder
4. Add medical images in images/ folder
5. Process with: python process_clinical_folder.py path/to/this/folder
