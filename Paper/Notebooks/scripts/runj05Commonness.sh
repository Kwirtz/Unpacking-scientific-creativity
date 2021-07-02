#!/bin/bash
#SBATCH -n 1
module load python/python-3.6.0.i16
RUNPATH=$HOME/Taxonomy-of-novelty/Paper/Notebooks/scripts/
cd $RUNPATH
python HPC_commonness.py -year 2005 -var journal >> journalHPCCommonness_2005.log 2>&1