echo off

set OPENRADIOSS_PATH=%1
set sim_path=%2
set sim_file_name=%3
set number_of_threads=%4
set RAD_CFG_PATH=%OPENRADIOSS_PATH%\hm_cfg_files
set RAD_H3D_PATH=%OPENRADIOSS_PATH%\extlib\h3d\lib\win64
set PATH=%OPENRADIOSS_PATH%\extlib\hm_reader\win64;%PATH%
set PATH=%OPENRADIOSS_PATH%\extlib\intelOneAPI_runtime\win64;%PATH%
set KMP_STACKSIZE=400m
cd %sim_path%
%OPENRADIOSS_PATH%\exec\starter_win64.exe -i %sim_path%\%sim_file_name%_0000.rad -nt %number_of_threads% -np 1
%OPENRADIOSS_PATH%\exec\engine_win64_sp.exe -i %sim_path%\%sim_file_name%_0001.rad -nt %number_of_threads% 