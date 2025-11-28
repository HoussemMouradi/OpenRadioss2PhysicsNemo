import sys
import os
import random
from vortex_radioss.animtod3plot.Anim_to_D3plot import readAndConvert


def format_radioss_field(value):
    try:
        formatted = "{:10.2f}".format(value)
        if len(formatted) > 10:
            # If it overflows
            formatted = "{:.2E}".format(value).replace('E', 'E+').replace('E+-', 'E-')
            if len(formatted) > 10:
                formatted = "{:.1E}".format(value).replace('E', 'E+').replace('E+-', 'E-')

        return formatted.rjust(10)
    except ValueError:
        return "        "

def modify_radioss_starter(input_filepath, output_filepath, prop_id_to_change, new_thickness):

    try:
        if not os.path.exists(input_filepath):
            print(f"Error: Input file not found at '{input_filepath}'")
            return

        with open(input_filepath, 'r') as infile, open(output_filepath, 'w') as outfile:

            in_prop_shell = False
            modifications_made = 0
            prop_id_str=""
            # Counter for lines inside /PROP/SHELL block (starts after /PROP/SHELL line)
            line_counter = 0
            modified_line = ""
            for line in infile:
                if line_counter!=7:
                    outfile.write(line)

                if line.strip().startswith('/PROP/SHELL/'):
                    in_prop_shell = True
                    prop_id_str = line[12:].strip()
                    print('SHELL PROP NUMBER: ', prop_id_str)
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

            print(f"\n--- Modification Complete ---")
            print(f"Total modifications made: {modifications_made}")
            if modifications_made == 0:
                print(f"Warning: /PROP/SHELL card with ID {prop_id_to_change} was not found or updated.")
            print(f"Output saved to: '{output_filepath}'")

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

def run_radioss(openradiosspath:str, simpath:str, simfile:str, nt:int):
    bat_file_directory = os.getcwd()
    os.system(bat_file_directory + "/runradioss.bat" + " " + openradiosspath + " " + simpath + " " + simfile + " " + str(nt))

def convert_anim_to_d3plot(resultfile_dir: str, resultfile: str):
    file_stem = resultfile_dir + "/" + resultfile
    readAndConvert(file_stem, use_shell_mask=False, silent=False)


if __name__ == "__main__":
    ########### MY INPUT ###########
     
    print("RADIOSS Shell Thickness Modifier")
    nt = 16
    sim_path = os.getcwd()
    openradioss_path = sim_path + "/OpenRadioss"
    sim_file = "Bumper_Beam_AP_meshed"
    prop_id = 2
    new_thickness = 2.2
    number_of_sims = 10
    os.mkdir(sim_path + "/RAW_DATA")
    for i in range(number_of_sims):
        
        if i < 10:
            sim_dir = sim_path + "/RAW_DATA" + "/Run10"+str(i)
        else:
            sim_dir = sim_path + "/RAW_DATA" + "/Run1"+str(i)
        os.mkdir(sim_dir)
        new_thickness = random.uniform(1.0, 5.0)

        new_thickness_str=f"{new_thickness:.2f}".replace('.', '_')
        master_sim_file = sim_path + "/" + sim_file + "_0000.rad"
        master_engine_file_with_path = sim_path + "/" + sim_file + "_0001.rad"
        new_sim_file = sim_file + "_" + new_thickness_str
        new_sim_path = sim_dir + "/" + new_sim_file
        new_sim_file_with_path = new_sim_path+"_0000.rad"
        new_engine_file_with_path = new_sim_path+"_0001.rad"


        modify_radioss_starter(master_sim_file,new_sim_file_with_path, 2, new_thickness)
        copy_engine_file(master_engine_file_with_path,new_engine_file_with_path)
        

        run_radioss(openradioss_path, sim_dir.replace("/", "\\") , new_sim_file, nt)
        convert_anim_to_d3plot(sim_dir,new_sim_file)

        
