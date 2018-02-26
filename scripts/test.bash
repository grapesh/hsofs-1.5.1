#!/bin/bash

export platform="/users/svinogra/mirrors/wcoss/surge"

export myModules=${platform}"/gpfs/hps3/nos/noscrub/nwprod/csdlpy-1.5.1"
export pythonCode=${platform}"/gpfs/hps3/nos/noscrub/nwprod/hsofs-1.5.1/hsofs/hsofs_post.py"
export logFile=${platform}"/gpfs/hps3/nos/noscrub/polar/hsofs/hsofs_post.log"

export hsofsDir=${platform}"/gpfs/hps/nco/ops/com/hsofs/prod/"
export stormID="al882018"
export stormCycle="2018022112"
export outputDir=${platform}"/gpfs/hps3/nos/noscrub/polar/hsofs/"
export tmpDir=${platform}"/gpfs/hps3/nos/noscrub/tmp/"
export pltCfgFile="/users/svinogra/mirrors/config.plot.hsofs.ini"

PYTHONPATH=${myModules} python -W ignore ${pythonCode} -i ${hsofsDir} -s ${stormID} -z ${stormCycle} -o ${outputDir} -t ${tmpDir} -p ${pltCfgFile} > ${logFile}
