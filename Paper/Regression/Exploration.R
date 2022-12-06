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

# Descriptives
#library(skimr)
library(stargazer)
library(corrplot)
# ML
library(xgboost)
library(caret)  



setwd("G:/Github/Taxonomy-of-novelty")
df <- read_csv("Data/regression.csv")
df$year <- as.factor(df$year)

summary(df)
unique(df$main_category)

novelty_cat <- c("New Finding", "Technical Advance","Interesting Hypothesis","Novel Drug Target")
variables <- c("nb_ref","year","nb_aut","journal_SJR","is_review","journal_age")
indicators <- c("uzzi_ref","uzzi_mesh","lee_ref","lee_mesh","foster_ref","foster_mesh","wang_ref","wang_mesh","shibayama_abstract","shibayama_title","author_intra_abstract","author_inter_abstract",
                "author_intra_title", "author_inter_title")
dependant <-  c("nb_cit","DI1","DI5","DI1nok","DeIn","Breadth","Depth","novel_f1000")

df <- df %>% mutate(novel_f1000 = ifelse(main_category %in% novelty_cat, 1, 0))

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
for (i in unique(df_f1000$main_category)){
  df_f1000[paste(i)] <- lengths(regmatches(df_f1000$categories, gregexpr(i,df_f1000$categories)))
  df_f1000[paste(i,"_binary")] <- ifelse(df_f1000[paste(i)] >= 1, 1, 0)
  f1000_cat <- append(f1000_cat,str_replace_all(i, c(" " = "_"  )))
  f1000_cat_binary <- append(f1000_cat_binary,str_replace_all(paste(i,"_binary"), c(" " = "_"  )))
}




names(df_f1000) <- str_replace_all(names(df_f1000), c(" " = "_"  ))
summary(df_f1000)

# Simple correlation

df_indicators = df[,append(indicators,dependant)] %>% drop_na()
df_indicators.cor = cor(df_indicators)
corrplot(df_indicators.cor)




# Logit ####

for (indicator in indicators){
  j = 0
  for (i in unique(df_f1000$main_category)){
    j <- j + 1
    name_col = str_replace_all(i, c(" " = "_"  ))
    nam <- paste("mod", j, sep = "_")
    print(name_col)
    df_temp <- df_f1000[,c(variables,c(name_col),c(paste(indicator)))] %>% drop_na()
    df_temp[name_col] <- as.factor(as.matrix(df_temp[name_col]))
    assign(nam, glm(substitute(i ~ ., list(i = as.name(name_col))),  data = df_temp, family ="binomial"))
  }
  
  underscore <- capture.output(
    stargazer(mod_1,mod_2,mod_3,mod_4,mod_5,mod_6,mod_7,mod_8,mod_9,mod_10,mod_11,
            keep.stat = c("n", "rsq"),
            keep = c('nb_ref','nb_aut','journal_SJR','is_review','journal_age'),
            out=paste("Result/Regression/logit_", indicator,".tex")))
}

# Poisson ####

j = 0
for (i in unique(df_f1000$main_category)){
  j <- j + 1
  name_col = str_replace_all(i, c(" " = "_"  ))
  nam <- paste("mod", j, sep = "_")
  print(name_col)
  df_temp <- df_f1000[,c(variables,c(name_col),c('wang_ref'))] %>% drop_na()
  df_temp[name_col] <- as.factor(as.matrix(df_temp[name_col]))
  assign(nam, glm(substitute(i ~ ., list(i = as.name(name_col))),  data = df_temp, family ="binomial"))
}


mod_1 <- glm(New_Finding~wang_mesh, data = df_f1000, family ="poisson")
mod_2 <- glm(New_Finding~wang_ref, data = df_f1000, family ="poisson")
mod_3 <- glm(New_Finding~wang_ref + wang_mesh, data = df_f1000, family ="poisson")
stargazer(mod_1, mod_2, mod_3, keep.stat = c("n", "rsq"))


summary(glm(main_category~wang_mesh, data = df_f1000, family = "binomial"))
summary(glm(main_category~wang_ref, data = df_f1000, family = "binomial"))
summary(glm(main_category~foster_mesh, data = df_f1000, family = "binomial"))
summary(glm(main_category~foster_ref, data = df_f1000, family = "binomial"))
summary(glm(main_category~foster_mesh, data = df_f1000, family = "binomial"))


summary(lm(main_category~wang_mesh, data = df_f1000))


# NB ####
summary(m1 <- glm.nb(daysabs ~ math + prog, data = dat))

# XGBOOST ####

df_result = 

for(cat in f1000_cat_binary){
    accuracies = c()
    for(i in append(c(1),indicators)){
      
      parts = createDataPartition(as.matrix(df_f1000[,cat]), p = 0.8, list = F)
      train = df_f1000[parts, ]
      test = df_f1000[-parts, ]
      if (i == "1"){
      X_names <- c("nb_ref","year","nb_aut","journal_SJR")
      }
      else{
        X_names <- append(c("nb_ref","year","nb_aut","journal_SJR"),c(i))
      }
      X_train = data.matrix(train[,X_names])
      y_train = data.matrix(train[,cat])
      
      X_test = data.matrix(test[,X_names])
      y_test = data.matrix(test[,cat]) 
    
      # convert the train and test data into xgboost matrix type.
      xgboost_train = xgb.DMatrix(data=X_train, label=y_train)
      xgboost_test = xgb.DMatrix(data=X_test, label=y_test)
      
      model <- xgboost(data = xgboost_train,                    # the data   
                       max.depth=3,                        # max depth 
                       nrounds=50)                              # max number of boosting iterations
      
      summary(model)
      
      pred_test = predict(model, xgboost_test)
      
      pred_test  
    
      pred_test[(pred_test>=0.80)] = 1
      pred_test[(pred_test<0.80)] = 0  
    
      conf_mat = confusionMatrix(as.factor(y_test), as.factor(pred_test))
      #accuracies = append(accuracies, conf_mat$overall['Accuracy'])
      #precision <- conf_mat$byClass['Pos Pred Value']    
      #recall <- conf_mat$byClass['Sensitivity']  
      accuracies = append(accuracies, conf_mat$byClass['Balanced Accuracy'] )

    }  
    df[cat] = accuracies
}

df

#precision <- conf_mat$byClass['Pos Pred Value']    
#recall <- conf_mat$byClass['Sensitivity']
# Interpretation guidelines 
