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
library(ggplot2)

#setwd("G:/Github/Taxonomy-of-novelty")
setwd("C:/Users/kevin/Documents/GitHub/Taxonomy-of-novelty")

df <- read_csv("Data/regression.csv")


ggplot(df %>%drop_na(count_diverse), aes(x=share_diverse, y=nb_cit)) +
  geom_point(size=2, shape=23)

ggplot(df %>%na.omit("nb_aut"), aes(x=nb_aut, y=nb_cit)) +
  geom_point(size=2, shape=23)


test = df %>%
  drop_na(share_diverse,nb_cit,nb_aut) %>%
  mutate(nb_cit_weighted = nb_cit/nb_aut) %>%
  group_by(share_diverse) %>%
  summarise(across(nb_cit_weighted, mean, na.rm = TRUE))

