#!/bin/bash
#SBATCH -n 1
module load python/python-3.6.0.i16
RUNPATH=$HOME/Taxonomy-of-novelty/Paper/Notebooks/scripts/
cd $RUNPATH
python HPC_atypicality.py -year 2007 -var journal -load False -nb_sample 20 >> journalHPCAtypicality_2007.log 2>&1