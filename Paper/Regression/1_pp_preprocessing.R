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
library(data.table)
library(plotly)
# Descriptives
#library(skimr)
library(stargazer)
library(corrplot)
library(dplyr)
library(ks)

#setwd("G:/Github/Taxonomy-of-novelty")
#setwd("C:/Users/kevin/Documents/GitHub/Taxonomy-of-novelty")


df = fread('Data/regression.csv')
df = unique(df, by = 'PMID')

#########################################

# Hangle multiple category for journals

#multiple_cat = df[,.(cat= unlist(tstrsplit(journal_category, "; ", type.convert = TRUE)))]
#multiple_cat[,cat:= gsub(' \\(Q\\d\\)$','',cat)]
#length(unique(multiple_cat$cat)) # 303

# va y nique on prend la premiere cat

df[,journal_main_cat := strsplit(journal_category, "; ")[[1]][1], by = 'PMID']
df[,journal_main_cat := gsub(' \\(Q\\d\\)$','',journal_main_cat)]
length(unique(df$journal_main_cat))
#271

# 
########################################"
summary(df)
unique(df$main_category)

novelty_cat <- c("New Finding", "Technical Advance","Interesting Hypothesis","Novel Drug Target")
variables <- c("nb_ref","year","nb_aut","journal_SJR")

indicators <- c("uzzi_mesh","lee_mesh","foster_mesh","wang_mesh",
                "uzzi_ref","lee_ref","foster_ref","wang_ref",
                "shibayama_abstract","shibayama_title",
                "author_intra_abstract","author_inter_abstract",
                "author_intra_title", "author_inter_title")
indicators_fw <- paste0(indicators, "_fw")
dependant <-  c("nb_cit","DI1","DI5","DI1nok","DeIn","Breadth","Depth")
dependant_fw <- paste0(dependant, "_fw")

df <- df %>% mutate(novel_f1000 = ifelse(main_category %in% novelty_cat, 1, 0))
df <- df %>% filter(nb_ref>1 & nb_meshterms>1 & nb_aut>1)

df %<>%
  group_by(journal_main_cat, year) %>%
  mutate(nb_cit_fw = nb_cit %>% percent_rank(),
         wang_mesh_fw = wang_mesh %>% percent_rank(),
         wang_ref_fw = wang_ref %>% percent_rank(),
         uzzi_mesh = -uzzi_mesh,
         uzzi_ref = -uzzi_ref,
         uzzi_mesh_fw = uzzi_mesh %>% percent_rank(),
         uzzi_ref_fw = uzzi_ref %>% percent_rank(),
         foster_mesh_fw = foster_mesh %>% percent_rank(),
         foster_ref_fw = foster_ref %>% percent_rank(),
         lee_mesh_fw = lee_mesh %>% percent_rank(),
         lee_ref_fw = lee_ref %>% percent_rank(),
         shibayama_abstract_fw = shibayama_abstract %>% percent_rank(),
         shibayama_title_fw = shibayama_title %>% percent_rank(),
         author_intra_abstract_fw = author_intra_abstract %>% percent_rank(),
         author_inter_abstract_fw = author_inter_abstract %>% percent_rank(),
         author_intra_title_fw = author_intra_title %>% percent_rank(),
         author_inter_title_fw = author_inter_title %>% percent_rank(),
         DI5_fw = DI5 %>% percent_rank(),
         DI1_fw = DI1 %>% percent_rank(),
         DI1nok_fw = DI1nok %>% percent_rank(),
         DeIn_fw = DeIn %>% percent_rank(),
         Breadth_fw = Breadth %>% percent_rank(),
         Depth_fw = Depth %>% percent_rank(),
  ) %>%
  ungroup()

fwrite(df,'Data/reg_df.csv')