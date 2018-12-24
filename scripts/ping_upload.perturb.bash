#!/bin/bash

YYYYMMDD=$1
CY=$2
if [ -e /gpfs/hps3/nos/noscrub/Yuji.Funakoshi/Dev-hsofs.v2.0.1/com/hsofs/test/hsofs.${YYYYMMDD}/*${YYYYMMDD}${CY}*022*.surfaceforcing ]; then
    startFile=/gpfs/hps3/nos/noscrub/nwprod/hsofs-1.5.1/scripts/done.perturb.${YYYYMMDD}${CY}.txt 
    if [ ! -e ${startFile} ] ; then
        date > ${startFile}
        /gpfs/hps3/nos/noscrub/nwprod/hsofs-1.5.1/scripts/test_perturb.bash ${YYYYMMDD}${CY} 
    fi
fi


