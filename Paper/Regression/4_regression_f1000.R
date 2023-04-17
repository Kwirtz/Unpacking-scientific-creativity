
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
library(data.table)
library(caret)  
library(caTools)
library(e1071)
library(dplyr)

indicators <- c("uzzi_ref","uzzi_mesh","lee_ref","lee_mesh","foster_ref","foster_mesh",
                "wang_ref","wang_mesh","shibayama_abstract","shibayama_title")
indicators_fw <- paste0(indicators, "_fw")

df = fread('reg_df.csv')

df_f1000 <- as_tibble(df) %>% 
  filter(main_category != '')

todummy = df_f1000 %>% separate_rows(categories,sep = '\\n')
todummy = todummy %>% group_by(PMID,categories) %>% summarise(nb_cat = n())

#define one-hot encoding function
dummy <- dummyVars(" ~ .", data=todummy)
final_df <- data.frame(predict(dummy, newdata=todummy))
colnames(final_df)[2:13] = gsub('categories','',colnames(final_df)[2:13])
final_df = final_df %>%
  mutate(across(all_of(colnames(final_df)[2:13]), ~ . * nb_cat, .names = "{.col}")) %>% 
  group_by(PMID) %>% dplyr::select(-nb_cat) %>% 
  summarise(across(all_of(colnames(final_df)[2:13]), sum, .names = "{.col}"))

df_f1000 = left_join(df_f1000,final_df)
df_f1000 = as.data.table(df_f1000)

reg = function(dependant,sq,int,fw,higly_exp = F,logit,novelty,independant){
  if(fw){
    dependant = paste0(dependant)
    independant = 'author_inter_abstract_fw + author_intra_abstract_fw'
    independant_sq = 'I(author_inter_abstract_fw**2) + I(author_intra_abstract_fw**2)'
    independant_inter = 'I(author_inter_abstract_fw*author_intra_abstract_fw)'
    vars_ = c("nb_ref",
              "nb_aut",
              'nb_meshterms',
              #"sum_deg_cen_cumsum",
              "year",
              "journal_main_cat",
              "share_diverse",
              "share_typical",
              "journal_SJR",
              "author_inter_abstract_fw",
              "author_intra_abstract_fw",
              "Journal_ISSN",
              dependant)
  }else{
    if(novelty){
      independant = independant
    }else{
      independant = 'author_inter_abstract + author_intra_abstract'
      independant_sq = 'I(author_inter_abstract**2) + I(author_intra_abstract**2)'
      independant_inter = 'I(author_inter_abstract*author_intra_abstract)'
    }
    vars_ = c("nb_ref",
              "nb_aut",
              'nb_meshterms',
              #"sum_deg_cen_cumsum",
              "year",
              "journal_main_cat",
              "share_diverse",
              "share_typical",
              "journal_SJR",
              "author_inter_abstract",
              "author_intra_abstract",
              "Journal_ISSN",
              dependant,
              independant)
  }
  
  tmp = na.omit(df_f1000[,..vars_])
  tmp = tmp[journal_main_cat != ""]
  tmp = tmp[Journal_ISSN != ""]
  controls = 'nb_ref + nb_meshterms + nb_aut + as.factor(year) + journal_main_cat + journal_SJR'
  if(sq){
    if(int){
      formula_ = paste0(dependant," ~ ",independant," + ",independant_sq,' + ',independant_inter,' + ',controls)
    } else {
      formula_ = paste0(dependant," ~ ",independant," + ",independant_sq,' + ',controls)
    }
  } else {
    if(int){
      formula_ = paste0(dependant," ~ ",independant,' + ',independant_inter,' + ',controls)
    } else {
      formula_ = paste0(dependant," ~ ",independant," + ",controls)
    }
  }
  if(higly_exp){
    if(fw){
      formula_ = gsub('author_intra_abstract_fw','share_diverse',formula_)
      if(sq){
        formula_ = gsub('I\\(share_diverse\\*\\*2\\)','share_typical \\+ I(share_diverse*share_typical)',formula_)
      } else {
        formula_ = gsub('share_diverse','share_diverse \\+ share_typical \\+ I(share_diverse*share_typical)',formula_)
      }
    }else{
      formula_ = gsub('author_intra_abstract','share_diverse',formula_)
      if(sq){
        formula_ = gsub('I\\(share_diverse\\*\\*2\\)','share_typical \\+ I(share_diverse*share_typical)',formula_)
      } else {
        formula_ = gsub('share_diverse','share_diverse \\+ share_typical \\+ I(share_diverse*share_typical)',formula_)
      }
    }
  }
  print(formula_)
  if(logit){
    tmp[,(dependant) := ifelse(get(dependant)>0,1,0)]
    model = glm(formula = as.formula(formula_), 
                data = tmp, family=binomial(link = "logit"))
  } else {
    model = glm(formula = as.formula(formula_), 
                data = tmp, family="poisson")
  }
  vcov_cluster <- sandwich::vcovCL(model, cluster = tmp$Journal_ISSN)
  return(list(model,vcov_cluster))
}

get_table = function(all_dep,title,sq,int,fw,higly_exp=F,logit,novelty = F,independant=F){
  
  models = list()
  cov = list()
  for(i in 1:length(all_dep)){
    model = reg(dependant = all_dep[i],
                sq = sq,
                int = int,
                fw = fw,
                higly_exp = higly_exp,
                logit = logit,
                novelty = novelty,
                independant= independant)
    models[[i]] = model[[1]]
    cov[[i]] = sqrt(diag(model[[2]]))
  }
  if(sq){
    title = paste0(title,'_sq')
  }
  if(int){
    title = paste0(title,'_int')
  }
  if(logit){
    title = paste0('logit_',title)
  } else {
    title = paste0('poisson_',title)
  }
  stargazer::stargazer(
    models, 
    se = cov,
    align = TRUE, type = "latex",
    keep = c(independant)#author_inter_abstract','author_intra_abstract','share_diverse',
            # "share_typical",'nb_aut','nb_ref','nb_meshterms','sum_deg_cen_cumsum','journal_SJR')
    #out = paste0(gsub(' ','_',title),'.tex')
  )
}


all_dep = c('New.Finding',                      
'Interesting.Hypothesis',           
'Technical.Advance',                
'Confirmation',                     
'Controversial')

tables = list()
for(i in 1:length(indicators_fw)){
  toclean = get_table(all_dep,
            'LOGIT- Cognitive dimension and Novelty',
            sq = F, 
            int = F,
            fw = F,
            logit = F,
            novelty = T,
            independant = indicators_fw[i])[16:20]
  n = strsplit(toclean[5],split = '\\{')[[1]][4]
  n = strsplit(n,'\\}')[[1]][1]
  toclean[1] = paste0(toclean[1],' & ',n)
tables[[i]] = toclean[1:4]
}



get_table(all_dep,
          'LOGIT- Cognitive dimension and Novelty',
          sq = F, 
          int = F,
          fw = F,
          logit = T)


get_table(all_dep,
          'LOGIT - Cognitive dimension and Novelty',
          sq = T, 
          int = F,
          fw = F,
          logit = T)


get_table(all_dep,
          'LOGIT - Cognitive dimension and Novelty',
          sq = F, 
          int = F,
          fw = T,
          logit = T)

get_table(all_dep,
          'LOGIT - Cognitive dimension and Novelty',
          sq = T, 
          int = F,
          fw = T,
          logit = T)




#---------------------


get_table(all_dep,
          'POISSON - Cognitive dimension and Novelty',
          sq = F, 
          int = F,
          fw = F,
          logit = F)


get_table(all_dep,
          'POISSON - Cognitive dimension and Novelty',
          sq = T, 
          int = F,
          fw = F,
          logit = F)


get_table(all_dep,
          'POISSON - Cognitive dimension and Novelty',
          sq = F, 
          int = F,
          fw = T,
          logit = F)

get_table(all_dep,
          'POISSON - Cognitive dimension and Novelty',
          sq = T, 
          int = F,
          fw = T,
          logit = F)

#---------------------



get_table(all_dep,
          'LOGIT-Cognitive diversity, Share of higly exploratory individuals and Novelty ',
          sq = F, 
          int = F,
          fw = F,
          logit = T,
          higly_exp = T)


get_table(all_dep,
          'LOGIT -Cognitive diversity, Share of higly exploratory individuals and Novelty ',
          sq = T, 
          int = F,
          fw = F,
          logit = T,
          higly_exp = T)


get_table(all_dep,
          'LOGIT -Cognitive diversity, Share of higly exploratory individuals and Novelty ',
          sq = F, 
          int = F,
          fw = T,
          logit = T,
          higly_exp = T)

get_table(all_dep,
          'LOGIT -Cognitive diversity, Share of higly exploratory individuals and Novelty ',
          sq = T, 
          int = F,
          fw = T,
          logit = T,
          higly_exp = T)




#---------------------


get_table(all_dep,
          'POISSON - Cognitive diversity, Share of higly exploratory individuals and Novelty ',
          sq = F, 
          int = F,
          fw = F,
          logit = F,
          higly_exp = T)


get_table(all_dep,
          'POISSON - Cognitive diversity, Share of higly exploratory individuals and Novelty ',
          sq = T, 
          int = F,
          fw = F,
          logit = F,
          higly_exp = T)


get_table(all_dep,
          'POISSON - Cognitive diversity, Share of higly exploratory individuals and Novelty ',
          sq = F, 
          int = F,
          fw = T,
          logit = F,
          higly_exp = T)

get_table(all_dep,
          'POISSON - Cognitive diversity, Share of higly exploratory individuals and Novelty ',
          sq = T, 
          int = F,
          fw = T,
          logit = F,
          higly_exp = T)

