#!/bin/bash
#SBATCH -n 1
module load python/python-3.6.0.i16
RUNPATH=$HOME/Taxonomy-of-novelty/Paper/Notebooks/scripts/
cd $RUNPATH
python HPC_atypicality.py -year 2001 -var mesh -load False -nb_sample 20 >> meshHPCAtypicality_2001.log 2>&1