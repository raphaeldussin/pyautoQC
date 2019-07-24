#!/bin/bash

. $HOME/.bashrc
conda activate devQC

source_id=GFDL-CM4
exp_id=piControl
var=tos
grid=gr1
dirtag=/data_cmip6/CMIP6/CMIP/NOAA-GFDL/${source_id}/${exp_id}/r1i1p1f1/3hr/tos/gr1/v20190201 
dirout=/work/Raphael.Dussin/QC_results/${source_id}-${exp_id}_3hr_gr1

files=$( ls $dirtag/*.nc  )

for file in $files ; do
  echo working on file $file 
     time qc_check_data -l $file -v $var -t 1 -x lon -y lat -z lev -w 6 -o $dirout
     rm -f slurm*out
done

qc_postcheck_data -l $dirout/QC_${source_id}-${exp_id}_${grid}_mean_${var}*.nc -v ${var} -z lev


