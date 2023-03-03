# Knitr options
### Generic preamble
rm(list = ls(all.names = TRUE)) #will clear all objects includes hidden objects.
gc() #free up memrory and report the memory usage.
graphics.off()

Sys.setenv(LANG = "en") # For english language
options(scipen = 5) # To deactivate annoying scientific number notation

### Load packages
library(tidyverse) # Collection of all the good stuff like dplyr, ggplot2 ect.
library(magrittr) # For extra-piping operators (eg. %<>%)
library(glue)
# Descriptives
#library(skimr)
library(stargazer)
library(corrplot)

#setwd("G:/Github/Taxonomy-of-novelty")
setwd("C:/Users/kevin/Documents/GitHub/Taxonomy-of-novelty")

df <- read_csv("Data/regression.csv")