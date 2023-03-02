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
# ML
library(xgboost)
library(caret)  
library(caTools)
library(e1071)

#setwd("G:/Github/Taxonomy-of-novelty")
setwd("C:/Users/kevin/Documents/GitHub/Taxonomy-of-novelty")

df <- read_csv("Data/regression.csv")
df$year <- as.factor(df$year)

summary(df)
unique(df$main_category)

novelty_cat <- c("New Finding", "Technical Advance","Interesting Hypothesis","Novel Drug Target")
variables <- c("nb_ref","year","nb_aut","journal_SJR","is_review","journal_age")
indicators <- c("uzzi_ref","uzzi_mesh","lee_ref","lee_mesh","foster_ref","foster_mesh","wang_ref","wang_mesh","shibayama_abstract","shibayama_title","author_intra_abstract","author_inter_abstract",
                "author_intra_title", "author_inter_title")
indicators_fw <- paste0(indicators, "_fw")
dependant <-  c("nb_cit","DI1","DI5","DI1nok","DeIn","Breadth","Depth")
dependant_fw <- paste0(dependant, "_fw")

df <- df %>% mutate(novel_f1000 = ifelse(main_category %in% novelty_cat, 1, 0))

df %<>%
  group_by(journal_category, year) %>%
  mutate(nb_cit_fw = nb_cit %>% percent_rank(),
         wang_mesh_fw = wang_mesh %>% percent_rank(),
         wang_ref_fw = wang_ref %>% percent_rank(),
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

df_f1000 <- df %>% 
  drop_na(main_category)

df_f1000 %>% count(year) %>%
  ggplot(aes(x = year, y = n)) + 
  geom_col() +
  theme_classic() + 
  ggtitle("Number of papers matched with F1000 2000-2005") +
  theme(plot.title = element_text(hjust = 0.5))


# Each column = a cat

f1000_cat = c()
f1000_cat_binary = c()
f1000_cat_restricted = c("New_Finding","Novel_Drug_Target","Controversial","Technical_Advance")

for (i in unique(df_f1000$main_category)){
  df_f1000[paste(i)] <- lengths(regmatches(df_f1000$categories, gregexpr(i,df_f1000$categories)))
  df_f1000[paste(i,"_binary")] <- ifelse(df_f1000[paste(i)] >= 1, 1, 0)
  f1000_cat <- append(f1000_cat,str_replace_all(i, c(" " = "_","/"="_",":"="_")))
  f1000_cat_binary <- append(f1000_cat_binary,str_replace_all(paste(i,"_binary"), c(" " = "_","/"="_",":"="_")))
}




names(df_f1000) <- str_replace_all(names(df_f1000), c(" " = "_","/"="_",":"="_"))
names(df_f1000) <- str_replace_all(names(df_f1000), c(" " = "_","/"="_",":"="_"))
summary(df_f1000)
df_f1000[,f1000_cat_binary] <- lapply(df_f1000[,f1000_cat_binary],as.factor)

# Simple correlation

df_indicators = df[,append(indicators_fw,dependant_fw)] %>% drop_na()
df_indicators.cor = cor(df_indicators)
corrplot(df_indicators.cor)

saveRDS(df_f1000, file = "Data/regression_data.rds")

plot(data=df_f1000,x=nb_aut, y=author_intra_title_fw)

ggplot(data=df_f1000[df_f1000$nb_aut < 50, ] , aes(x=nb_aut, y=uzzi_ref_fw)) + 
  geom_point()
