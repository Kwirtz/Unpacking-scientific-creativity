#!/bin/bash

#SBATCH -n 1
#SBATCH -t 10:00:00

module load python/Anaconda3-2019
RUNPATH=$HOME/Taxonomy-of-novelty
cd $RUNPATH
python3 Paper/Notebooks/scripts/create_our_indicator.py --date year --year 1981 --var CR_year_category --start 0 --end 500 >> our_indicator.log 2>&1