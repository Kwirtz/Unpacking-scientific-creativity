#!/bin/bash
#SBATCH -n 1
module load python/python-3.6.0.i16
RUNPATH=$HOME/Taxonomy-of-novelty/Paper/Notebooks/scripts/
cd $RUNPATH
python HPC_novelty.py -year 2006 -var mesh >> meshHPCNovelty_2006.log 2>&1