#!/bin/bash
# OpenRadioss Linux Run Script

OPENRADIOSS_PATH=$1
sim_path=$2
sim_file_name=$3
number_of_threads=$4

export RAD_CFG_PATH=${OPENRADIOSS_PATH}/hm_cfg_files
export RAD_H3D_PATH=${OPENRADIOSS_PATH}/extlib/h3d/lib/linux64
export LD_LIBRARY_PATH=${OPENRADIOSS_PATH}/extlib/hm_reader/linux64:${LD_LIBRARY_PATH}
export OMP_STACKSIZE=400m

cd ${sim_path}

# Run starter (pre-processor): reads the _0000.rad input deck and prepares the model
${OPENRADIOSS_PATH}/exec/starter_linux64_gf -i ${sim_path}/${sim_file_name}_0000.rad -nt ${number_of_threads} -np 1

# Run engine (solver): reads the _0001.rad control deck and runs the time-marching simulation
${OPENRADIOSS_PATH}/exec/engine_linux64_gf_sp -i ${sim_path}/${sim_file_name}_0001.rad -nt ${number_of_threads}
