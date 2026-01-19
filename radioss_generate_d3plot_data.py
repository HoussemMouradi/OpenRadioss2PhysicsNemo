import sys
import time
import os
import random
from vortex_radioss.animtod3plot.Anim_to_D3plot import readAndConvert
import pyfiglet


def format_radioss_field(value):
    try:
        # Try to format as standard float with 4 decimal places
        formatted = "{:10.2f}".format(value)
        if len(formatted) > 10:
            # If it overflows, use 8-character scientific notation (e.g., 1.23E+04)
            formatted = "{:.2E}".format(value).replace('E', 'E+').replace('E+-', 'E-')
            if len(formatted) > 10:
                # If still too long, fall back to a trimmed scientific format
                formatted = "{:.1E}".format(value).replace('E', 'E+').replace('E+-', 'E-')

        # Ensure it is exactly 10 characters wide (right-justified)
        return formatted.rjust(10)
    except ValueError:
        # Handle non-numeric input gracefully
        return "        " # 10 spaces

def modify_radioss_deck(input_filepath, output_filepath, prop_id_to_change, new_thickness):

    try:
        # Check if the input file exists
        if not os.path.exists(input_filepath):
            print(f"Error: Input file not found at '{input_filepath}'")
            return

        with open(input_filepath, 'r') as infile, open(output_filepath, 'w') as outfile:

            in_prop_shell = False
            modifications_made = 0
            prop_id_str="9999"
            # Counter for lines inside the /PROP/SHELL block (starts after /PROP/SHELL line)
            line_counter = 0
            modified_line = ""
            for line in infile:
                if line_counter!=7:
                    outfile.write(line)

                if line.strip().startswith('/PROP/SHELL/'):
                    in_prop_shell = True
                    prop_id_str = line[12:].strip()
                    #print('SHELL PROP NUMBER: ', prop_id_str)
                if  int(prop_id_str)==prop_id_to_change:
                    if line_counter<=8 and in_prop_shell:
                        line_counter+=1
                        in_prop_shell = True
                    else:
                        line_counter=0
                        in_prop_shell=False

                if line_counter==8:
                    line_counter=0
                    in_prop_shell = False
                    modified_line=line[:30]+format_radioss_field(new_thickness)+line[40:]
                    outfile.write(modified_line)
                    modifications_made+=1

            #print(f"\n--- Modification Complete ---")
            #print(f"Total modifications made: {modifications_made}")
            if modifications_made == 0:
                print(f"Warning: /PROP/SHELL card with ID {prop_id_to_change} was not found or updated.")
            #print(f"Output saved to: '{output_filepath}'")

    except FileNotFoundError:
        print(f"Error: Could not open one of the files.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def copy_engine_file(master_engine_file_with_path, new_engine_file_with_path):

    try:
        # Check if the input file exists
        if not os.path.exists(master_engine_file_with_path):
            print(f"Error: Input file not found at '{master_engine_file_with_path}'")
            return

        with open(master_engine_file_with_path, 'r') as infile, open(new_engine_file_with_path, 'w') as outfile:

            for line in infile:
                    outfile.write(line)
    except FileNotFoundError:
        print(f"Error: Could not open one of the files.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def run_radioss(openradiosspath:str, simpath:str, simfile:str):
    os.system("C:/Users/hmouradi/Documents/bumper_beam_physicsnemo/runradioss.bat" + " " + openradiosspath + " " + simpath + " " + simfile)

def convert_anim_to_d3plot(resultfile_dir: str, resultfile: str):
    file_stem = resultfile_dir + "/" + resultfile
    readAndConvert(file_stem, use_shell_mask=False, silent=False)


if __name__ == "__main__":
    ########### MY INPUT ###########
    print(pyfiglet.figlet_format("D3PLOT  DATA", justify="center",width=110))
    print(pyfiglet.figlet_format("PREPARATION", font='speed', justify="center",width=110))
    print(pyfiglet.figlet_format("POWERED  BY", justify="center",width=110))
    print(pyfiglet.figlet_format("OpenRadioss", font='speed', justify="center",width=110))
    
    time.sleep(3)


    openradioss_path = "C:/OpenRadioss"
    sim_path = os.getcwd()
    sim_file = "Bumper_Beam_AP_meshed"
    prop_id = 2
    new_thickness = 2.2
    number_of_sims = 3
    os.mkdir(sim_path + "/RAW_DATA")
    for i in range(number_of_sims):
        if i < 10:
            run_dir = sim_path + "/RAW_DATA" + "/Run10" + str(i)
        else:
            run_dir = sim_path + "/RAW_DATA" + "/Run1" + str(i)
        os.mkdir(run_dir)
        new_thickness = random.uniform(1.0, 5.0)

        new_thickness_str=f"{new_thickness}".replace('.', '_')
        master_sim_file = sim_path + "/" + sim_file + "_0000.rad"
        master_engine_file_with_path = sim_path + "/" + sim_file + "_0001.rad"
        new_sim_file = sim_file
        new_sim_path = run_dir + "/" + new_sim_file
        new_sim_file_with_path = new_sim_path+"_0000.rad"
        new_engine_file_with_path = new_sim_path+"_0001.rad"


        modify_radioss_deck(master_sim_file,new_sim_file_with_path, 2, new_thickness)
        copy_engine_file(master_engine_file_with_path,new_engine_file_with_path)
        

        run_radioss(openradioss_path, run_dir, new_sim_file)
        convert_anim_to_d3plot(run_dir,new_sim_file)
