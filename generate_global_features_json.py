import os
import json
from pathlib import Path

def parse_rad_file(filepath):
    """Parses a single 0000.rad file and extracts simulation parameters."""
    data = {}
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

    for i, line in enumerate(lines):
        line = line.strip()
        
        # 1. Initial Velocity (velocity_x)
        if line.startswith('/INIVEL/TRA/1'):
            for j in range(i+1, len(lines)):
                if lines[j].startswith('/'): break # Stop if next block starts
                if 'Vx' in lines[j] and 'Vy' in lines[j]:
                    val_line = lines[j+1].split()
                    try:
                        data['velocity_x'] = float(val_line[0])
                    except (IndexError, ValueError):
                        print(f"Warning: Could not parse velocity_x in {filepath}")
                    break
                    
        # 2. Rigid Wall Origin Y (rwall_origin_y)
        elif line.startswith('/RWALL/CYL/1'):
            for j in range(i+1, len(lines)):
                if lines[j].startswith('/'): break # Stop if next block starts
                if 'XM' in lines[j] and 'YM' in lines[j]:
                    val_line = lines[j+1].split()
                    try:
                        # XM is 0, YM is 1
                        data['rwall_origin_y'] = float(val_line[1])
                    except (IndexError, ValueError):
                        print(f"Warning: Could not parse rwall_origin_y in {filepath}")
                    break
                    
        # 3. Shell Thickness (thickness_scale)
        elif line.startswith('/PROP/SHELL/2'):
            for j in range(i+1, len(lines)):
                if lines[j].startswith('/'): break # Stop if next block starts
                if 'Thick' in lines[j]:
                    val_line = lines[j+1].split()
                    try:
                        # N is 0, Istrain is 1, Thick is 2
                        data['thickness_scale'] = float(val_line[2])
                    except (IndexError, ValueError):
                        print(f"Warning: Could not parse thickness_scale in {filepath}")
                    break
    
    # Check for missing keys
    expected_keys = ['velocity_x', 'rwall_origin_y', 'thickness_scale']
    for k in expected_keys:
        if k not in data:
            print(f"Warning: Missing {k} in {filepath}")
            
    return data

def extract_simulation_data(base_dirs, output_file):
    """Iterates over base directories, extracts data from run folders, and saves to JSON."""
    results = {}
    
    for base_dir in base_dirs:
        base_path = Path(base_dir)
        if not base_path.exists():
            print(f"Warning: Directory '{base_dir}' does not exist. Skipping.")
            continue
        
        # Iterate through Run folders (e.g., Run100, Run101)
        for run_dir in base_path.iterdir():
            if run_dir.is_dir():
                # Look for any file ending in 0000.rad
                rad_files = list(run_dir.glob('*0000.rad'))
                if rad_files:
                    rad_file = rad_files[0]
                    parsed_data = parse_rad_file(rad_file)
                    if parsed_data:
                        results[run_dir.name] = parsed_data
                else:
                    print(f"Warning: Missing *0000.rad in '{run_dir}'")
                    
    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"\nExtraction complete. Data saved to '{output_file}'")

# --- Configuration and Execution ---
if __name__ == '__main__':
    # Set the paths to your directories here
    DIRECTORIES_TO_SCAN = [
        './TRAINING_DATA',
        './VALIDATION_DATA'
    ]
    OUTPUT_JSON_FILE = 'simulation_parameters.json'
    
    extract_simulation_data(DIRECTORIES_TO_SCAN, OUTPUT_JSON_FILE)