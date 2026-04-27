import sys
import os
import random
from vortex_radioss.animtod3plot.Anim_to_D3plot import readAndConvert


def format_radioss_field(value):
    try:
        formatted = "{:10.2f}".format(value)
        if len(formatted) > 10:
            formatted = "{:.2E}".format(value).replace('E', 'E+').replace('E+-', 'E-')
            if len(formatted) > 10:
                formatted = "{:.1E}".format(value).replace('E', 'E+').replace('E+-', 'E-')

        return formatted.rjust(10)
    except ValueError:
        return "        "

def modify_radioss_starter(input_filepath, output_filepath, prop_changes, pole_y_offset=None):
    """
    Modify multiple PROP/SHELL thicknesses and optionally pole Y position in a RADIOSS starter file.
    
    Args:
        input_filepath: Path to the input starter file
        output_filepath: Path to the output starter file
        prop_changes: Dictionary mapping prop_id to new_thickness, e.g., {2: 1.5, 3: 2.0}
        pole_y_offset: Optional float to add to the YM and Y_M1 values of /RWALL/CYL/1
    """
    try:
        if not os.path.exists(input_filepath):
            print(f"Error: Input file not found at '{input_filepath}'")
            return

        with open(input_filepath, 'r') as infile, open(output_filepath, 'w') as outfile:

            in_prop_shell = False
            in_rwall = False
            rwall_line_counter = 0
            modifications_made = {}
            prop_id_str = "9999999"
            line_counter = 0
            modified_line = ""
            
            for line in infile:
                # Check if this line should be skipped (will be replaced with modified version)
                skip_line = False
                
                # Handle /PROP/SHELL modifications
                if line.strip().startswith('/PROP/SHELL/'):
                    in_prop_shell = True
                    prop_id_str = line[12:].strip()
                    
                current_prop_id = int(prop_id_str)
                if current_prop_id in prop_changes:
                    if line_counter <= 8 and in_prop_shell:
                        line_counter += 1
                        in_prop_shell = True
                    else:
                        line_counter = 0
                        in_prop_shell = False

                    if line_counter == 8:
                        line_counter = 0
                        in_prop_shell = False
                        new_thickness = prop_changes[current_prop_id]
                        modified_line = line[:30] + format_radioss_field(new_thickness) + line[40:]
                        outfile.write(modified_line)
                        modifications_made[current_prop_id] = modifications_made.get(current_prop_id, 0) + 1
                        skip_line = True
                else:
                    if in_prop_shell:
                        line_counter = 0
                        in_prop_shell = False

                # Handle /RWALL/CYL/1 modifications
                if line.strip().startswith('/RWALL/CYL/1'):
                    in_rwall = True
                    rwall_line_counter = 0
                elif in_rwall:
                    rwall_line_counter += 1
                    
                    # Line 7: YM data line (columns 31-40, index 30-40)
                    if rwall_line_counter == 7 and pole_y_offset is not None:
                        # Parse the YM value from columns 31-40
                        ym_str = line[30:40].strip()
                        try:
                            ym_val = float(ym_str)
                            new_ym = ym_val + pole_y_offset
                            modified_line = line[:30] + format_radioss_field(new_ym) + line[40:]
                            outfile.write(modified_line)
                            modifications_made['pole_YM'] = True
                            skip_line = True
                        except ValueError:
                            pass  # Will write original line below
                    # Line 9: Y_M1 data line (columns 31-40, index 30-40)
                    elif rwall_line_counter == 9 and pole_y_offset is not None:
                        # Parse the Y_M1 value from columns 31-40
                        ym1_str = line[30:40].strip()
                        try:
                            ym1_val = float(ym1_str)
                            new_ym1 = ym1_val + pole_y_offset
                            modified_line = line[:30] + format_radioss_field(new_ym1) + line[40:]
                            outfile.write(modified_line)
                            modifications_made['pole_Y_M1'] = True
                            skip_line = True
                        except ValueError:
                            pass  # Will write original line below
                    elif rwall_line_counter >= 10:
                        in_rwall = False
                        rwall_line_counter = 0
                
                # Write the line if it wasn't skipped
                if not skip_line:
                    outfile.write(line)

            for prop_id in prop_changes:
                if prop_id not in modifications_made:
                    print(f"Warning: /PROP/SHELL card with ID {prop_id} was not found or updated.")
            
            if pole_y_offset is not None:
                if 'pole_YM' not in modifications_made:
                    print(f"Warning: Pole YM position was not found or updated.")
                if 'pole_Y_M1' not in modifications_made:
                    print(f"Warning: Pole Y_M1 position was not found or updated.")
            
            print(f"Run saved to: '{output_filepath}'")

    except FileNotFoundError:
        print(f"Error: Could not open one of the files.")
    except Exception as e:
        print(f"Oops! you have to deal with this: {e}")

def copy_engine_file(master_engine_file_with_path, new_engine_file_with_path):

    try:
        if not os.path.exists(master_engine_file_with_path):
            print(f"Error: Input file not found at '{master_engine_file_with_path}'")
            return

        with open(master_engine_file_with_path, 'r') as infile, open(new_engine_file_with_path, 'w') as outfile:

            for line in infile:
                    outfile.write(line)
    except FileNotFoundError:
        print(f"Error: Could not open one of the files.")
    except Exception as e:
        print(f"Oops! you have to deal with this: {e}")

def run_radioss(openradiosspath:str, simpath:str, simfile:str, nt:int):
    bat_file_directory = os.getcwd()
    os.system(bat_file_directory + "/runradioss.bat" + " " + openradiosspath + " " + simpath + " " + simfile + " " + str(nt))

def convert_anim_to_d3plot(resultfile_dir: str, resultfile: str):
    file_stem = resultfile_dir + "/" + resultfile
    readAndConvert(file_stem, use_shell_mask=False, silent=False)


if __name__ == "__main__":
     
    print("GENERATING D3PLOT DATASET FOR PhysicsNemo")
    print("       POWERED BY OpenRadioss")
    ###########################################################
    # Number of threads of your processor
    nt = 16
    sim_path = os.getcwd()
    # OpenRadioss path
    openradioss_path = sim_path + "/OpenRadioss"
    sim_name = "Bumper_Beam_AP_meshed"
    # Thickness range (min, max) - same for all props
    thickness_range = (1.2, 2.0)
    # List of PROP/SHELL IDs to modify with the same thickness
    prop_ids_to_change = [2, 7]
    # Add more prop IDs as needed
    # Pole Y position offset range (min, max)
    pole_y_range = (-500, 500)
    # Number of simulation runs
    number_of_sims = 7
    """""
    The generated data structure:

    ├── Run100/   
    │       ├── sim_name.d3plot
    │       ├── sim_name_0000.rad     # RADIOSS STARTER FILE
    │       └── sim_name_0001.rad     # RADIOSS ENGINE FILE
    ├── Run101/
    │       ├── sim_name.d3plot
    │       ├── sim_name_0000.rad
    │       └── sim_name_0001.rad
    └── ...
    """""
    ###########################################################

    os.mkdir(sim_path + "/RAW_DATA")
    for i in range(number_of_sims):
        
        if i < 10:
            run_dir = sim_path + "/RAW_DATA" + "/Run10"+str(i)
        else:
            run_dir = sim_path + "/RAW_DATA" + "/Run1"+str(i)
        os.mkdir(run_dir)
        
        # Generate one random thickness for all props
        new_thickness = random.uniform(thickness_range[0], thickness_range[1])
        prop_changes = {prop_id: new_thickness for prop_id in prop_ids_to_change}
        
        # Generate random pole Y offset
        pole_y_offset = random.uniform(pole_y_range[0], pole_y_range[1])

        master_starter_file = sim_path + "/" + sim_name + "_0000.rad"
        master_engine_file = sim_path + "/" + sim_name + "_0001.rad"

        new_starter_file = run_dir + "/" + sim_name + "_0000.rad"
        new_engine_file = run_dir + "/" + sim_name + "_0001.rad"


        modify_radioss_starter(master_starter_file, new_starter_file, prop_changes, pole_y_offset)
        copy_engine_file(master_engine_file, new_engine_file)
        

        run_radioss(openradioss_path, run_dir.replace("/", "\\") , sim_name, nt)
        convert_anim_to_d3plot(run_dir, sim_name)
