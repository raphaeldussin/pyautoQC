#!/bin/bash

. $HOME/.bashrc
conda activate devQC

source_id=GFDL-ESM4
exp_id=piControl
var=msftyz
grid=gn
dirtag=/data_cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-ESM4/piControl/r1i1p1f1/Omon/msftyz/gn/v20180701/
dirout=/work/Raphael.Dussin/QC_results/${source_id}-${exp_id}_Omon_gn_20191007

files=$( ls $dirtag/*.nc  )

for file in $files ; do
  echo working on file $file 
     time qc_check_data -l $file -v $var -t 1 -x lon -y lat -z lev -w 6 -o $dirout -c check.csv
     rm -f slurm*out
done

qc_postcheck_data -l $dirout/QC_${source_id}-${exp_id}_${grid}_mean_${var}*.nc -v ${var} -z lev


