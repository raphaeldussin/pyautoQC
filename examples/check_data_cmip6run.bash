#!/bin/bash

. $HOME/.bashrc
conda activate devQC

source_id=GFDL-ESM4
#exp_id=piControl
#exp_id=abrupt-4xCO2
exp_id=1pctCO2
onlypostcheck=False
dirrun=/data_cmip6/CMIP6/CMIP/NOAA-GFDL/${source_id}/${exp_id}/r1i1p1f1/Omon
dirout=/work/Raphael.Dussin/QC_results/${source_id}-${exp_id}_Omon
dirpng=/work/Raphael.Dussin/QC_results/${source_id}-${exp_id}_Omon/pngs
csvout=./csv/${source_id}-${exp_id}_Omon.csv

mkdir -p $dirout
mkdir -p $dirpng

listvar="thetao so volcello hfds sos tauuo tauvo tos"

for var in $listvar ; do

  dirvar=$dirrun/$var

  for grid in $( ls $dirvar ) ; do

    dirgrid=$dirvar/$grid

    for tag in $( ls $dirgrid ) ; do

      dirtag=$dirgrid/$tag

      files=$( ls $dirtag/*.nc | grep $var )

      echo working on var $var on grid $grid in tag $tag

      if [ $onlypostcheck != 'True' ] ; then
        # option 1: one test per file
        for file in $files ; do
          echo working on file $file 
          if [ $grid == gn ] ; then
             time qc_check_data -l $file -v $var -t 1 -x x -y y -z lev -w 2 -o $dirout -c $csvout
             rm -f slurm*out
          elif [ $grid == gr ] ; then
             time qc_check_data -l $file -v $var -t 1 -x lon -y lat -z lev -w 2 -o $dirout -c $csvout
             rm -f slurm*out
          elif [ $grid == gr1 ] ; then
             time qc_check_data -l $file -v $var -t 1 -x lon -y lat -z lev -w 2 -o $dirout -c $csvout
             rm -f slurm*out
          else
             echo PROBLEM: not sure how to treat grid $grid
          fi
        done
      fi

      tagout=${source_id}-${exp_id}_${grid} 
      echo checking for outliers in mean timeserie
      qc_postcheck_data -l $dirout/QC_${tagout}_mean_${var}*.nc -v ${var} -z lev -t ${tagout}_mean -o $dirpng
      echo checking for outliers in min timeserie
      qc_postcheck_data -l $dirout/QC_${tagout}_min_${var}*.nc -v ${var} -z lev -t ${tagout}_min -o $dirpng
      echo checking for outliers in max timeserie
      qc_postcheck_data -l $dirout/QC_${tagout}_max_${var}*.nc -v ${var} -z lev -t ${tagout}_max -o $dirpng

      # option 2: one global test (dask memory leak)
#     echo working on file $files
#     if [ $grid == gn ] ; then
#        time qc_check_data -l $files -v $var -t 1 -x x -y y -z lev -w 6
#     elif [ $grid == gr ] ; then
#        time qc_check_data -l $files -v $var -t 1 -x lon -y lat -z lev -w 4
#     else
#         echo not sure how to work with grid $grid
#     fi

    done # tag

  done #grid

done #var
