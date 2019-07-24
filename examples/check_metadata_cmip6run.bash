#!/bin/bash

. $HOME/.bashrc
conda activate devQC

dirrun=/data_cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-ESM4/piControl/r1i1p1f1/Omon

listvar="hfds so sos tauuo tauvo thetao tos volcello"

for var in $listvar ; do

  dirvar=$dirrun/$var

  for grid in $( ls $dirvar ) ; do

    dirgrid=$dirvar/$grid

    for tag in $( ls $dirgrid ) ; do

      dirtag=$dirgrid/$tag

      files=$( ls $dirtag/*.nc | grep $var )
      fileref=$( ls $dirtag/*.nc | grep $var  | head -1 )

      qc_check_metadata -l $files -r $fileref

    done # tag

  done #grid

done #var
