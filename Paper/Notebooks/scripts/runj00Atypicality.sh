#!/bin/bash
#SBATCH -n 1
source newenv/bin/activate
RUNPATH=$HOME/Taxonomy-of-novelty
cd $RUNPATH
python Paper/Notebooks/scripts/create_our_indicator.py -date year -year 1980 -var CR_year_category >> CR_year_category_our_1980.log 2>&1