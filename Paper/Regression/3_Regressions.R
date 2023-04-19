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
df_f1000 <- readRDS(file = "Data/regression_data.rds")

f1000_cat = c()
f1000_cat_binary = c()
f1000_cat_restricted = c("New_Finding","Novel_Drug_Target","Controversial","Technical_Advance")

for (i in unique(df_f1000$main_category)){
  df_f1000[paste(i)] <- lengths(regmatches(df_f1000$categories, gregexpr(i,df_f1000$categories)))
  df_f1000[paste(i,"_binary")] <- ifelse(df_f1000[paste(i)] >= 1, 1, 0)
  f1000_cat <- append(f1000_cat,str_replace_all(i, c(" " = "_","/"="_",":"="_")))
  f1000_cat_binary <- append(f1000_cat_binary,str_replace_all(paste(i,"_binary"), c(" " = "_","/"="_",":"="_")))
}

novelty_cat <- c("New Finding", "Technical Advance","Interesting Hypothesis","Novel Drug Target")
variables <- c("nb_ref","year","nb_aut","journal_SJR","is_review","journal_age")
indicators <- c("uzzi_ref","uzzi_mesh","lee_ref","lee_mesh","foster_ref","foster_mesh","wang_ref","wang_mesh","shibayama_abstract","shibayama_title","author_intra_abstract","author_inter_abstract",
                "author_intra_title", "author_inter_title")
indicators_fw <- paste0(indicators, "_fw")
dependant <-  c("nb_cit","DI1","DI5","DI1nok","DeIn","Breadth","Depth")
dependant_fw <- paste0(dependant, "_fw")

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

# SVM ####

df_temp <- df_f1000[,c("New_Finding__binary","nb_ref","year","nb_aut","journal_SJR")] %>% 
  drop_na()
df_f1000

split = sample.split(df_temp$New_Finding__binary, SplitRatio = 0.80)

training_set = subset(df_temp, split == TRUE)
test_set = subset(df_temp, split == FALSE)


classifier = svm(formula = New_Finding__binary ~ nb_ref+year+nb_aut+journal_SJR,
                 data = training_set,
                 type = 'C-classification',
                 kernel = 'linear')

y_pred = predict(classifier, newdata = test_set[-1])
y_true = as.factor(as.matrix(test_set[,"New_Finding__binary"]))
length(y_pred)
length(y_true)

caret::confusionMatrix(y_pred, y_true)

f1 <- function (data, lev = NULL, model = NULL) {
  precision <- posPredValue(data$pred, data$obs, positive = "pass")
  recall  <- sensitivity(data$pred, data$obs, postive = "pass")
  f1_val <- (2 * precision * recall) / (precision + recall)
  names(f1_val) <- c("F1")
  f1_val
} 

ctrl <- trainControl(method = "cv", number=10, savePred=T,summaryFunction = f1,)
mod <- train(New_Finding__binary ~ nb_ref+year+nb_aut+journal_SJR,
             data=df_temp, method = "svmLinear", trControl = ctrl)
unique(mod$pred$C)

#precision <- conf_mat$byClass['Pos Pred Value']    
#recall <- conf_mat$byClass['Sensitivity']
# Interpretation guidelines 

# clean Poisson no fw####

# \resizebox{\columnwidth}{!}{%

##### No CV 

for(cat_ in append(f1000_cat,"nb_cit")){
  mod_wang_1 <- glm(substitute(i ~ wang_mesh + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_wang_2 <- glm(substitute(i ~ wang_ref + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_wang_3 <- glm(substitute(i ~ wang_mesh + wang_ref + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_1 <- glm(substitute(i ~ uzzi_mesh + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_2 <- glm(substitute(i ~ uzzi_ref + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_3 <- glm(substitute(i ~ uzzi_mesh + uzzi_ref + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_1 <- glm(substitute(i ~ lee_mesh + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_2 <- glm(substitute(i ~ lee_ref + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_3 <- glm(substitute(i ~ lee_mesh + lee_ref + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_1 <- glm(substitute(i ~ foster_mesh + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_2 <- glm(substitute(i ~ foster_ref + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_3 <- glm(substitute(i ~ foster_mesh + foster_ref + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_1 <- glm(substitute(i ~ shibayama_abstract + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_2 <- glm(substitute(i ~ shibayama_title + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_3 <- glm(substitute(i ~ shibayama_abstract + shibayama_title + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  
  l = list(mod_wang_1, mod_wang_2, mod_wang_3, mod_uzzi_1, mod_uzzi_2, mod_uzzi_3,
           mod_lee_1, mod_lee_2, mod_lee_3, mod_foster_1, mod_foster_2, mod_foster_3,
           mod_shib_1,mod_shib_2,mod_shib_3
  )
  
  writeLines(capture.output(stargazer(l, font.size = "small", keep.stat = c("n", "rsq"),
                                      omit=append(variables ,c("Constant")),
                                      column.labels=c(cat_),
                                      dep.var.labels=c("","","","","","","","","","","","","","",""),
                                      model.names=FALSE,
                                      no.space=TRUE) ),
             glue("Results/Regressions/{cat_}.tex"))
}


# CV

for(cat_ in append(f1000_cat,"nb_cit")){
  mod_wang_1 <- glm(substitute(i ~ wang_mesh + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_wang_2 <- glm(substitute(i ~ wang_ref + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_wang_3 <- glm(substitute(i ~ wang_ref + wang_mesh + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_1 <- glm(substitute(i ~ uzzi_mesh+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_2 <- glm(substitute(i ~ uzzi_ref+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_3 <- glm(substitute(i ~ uzzi_ref + uzzi_mesh+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_1 <- glm(substitute(i ~ lee_mesh+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_2 <- glm(substitute(i ~ lee_ref+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_3 <- glm(substitute(i ~ lee_mesh + lee_ref+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_1 <- glm(substitute(i ~ foster_mesh+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_2 <- glm(substitute(i ~ foster_ref+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_3 <- glm(substitute(i ~ foster_mesh + foster_ref+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_1 <- glm(substitute(i ~ shibayama_abstract+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_2 <- glm(substitute(i ~ shibayama_title+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_3 <- glm(substitute(i ~ shibayama_abstract + shibayama_title + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  
  l = list(mod_wang_1, mod_wang_2, mod_wang_3, mod_uzzi_1, mod_uzzi_2, mod_uzzi_3,
           mod_lee_1, mod_lee_2, mod_lee_3, mod_foster_1, mod_foster_2, mod_foster_3,
           mod_shib_1,mod_shib_2,mod_shib_3
  )
  
  writeLines(capture.output(stargazer(l, font.size = "small", keep.stat = c("n", "rsq"),
                                      omit=append(variables ,c("Constant")),
                                      column.labels=c(cat_),
                                      dep.var.labels=c("","","","","","","","","","","","","","",""),
                                      model.names=FALSE,
                                      no.space=TRUE) ),
             glue("Results/Regressions/{cat_}_CV.tex"))
}

# Author no CV

for(cat_ in append(f1000_cat,"nb_cit")){
  mod_author_1 <- glm(substitute(i ~ author_intra_title + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_2 <- glm(substitute(i ~ author_inter_title + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_3 <- glm(substitute(i ~ author_intra_title + author_inter_title + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_4 <- glm(substitute(i ~ author_intra_abstract + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_5 <- glm(substitute(i ~ author_inter_abstract + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_6 <- glm(substitute(i ~ author_intra_abstract + author_inter_abstract + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_7 <- glm(substitute(i ~ author_intra_title + author_inter_title + author_intra_abstract + author_inter_abstract + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  
  
  l = list(mod_author_1, mod_author_2, mod_author_3, mod_author_4, mod_author_5,
           mod_author_6,mod_author_7)
  model_names = as.character(c(1:length((l))))
  writeLines(capture.output(stargazer(l,keep.stat = c("n", "rsq"),
                                      omit=append(variables ,c("Constant")),
                                      column.labels=c(cat_),
                                      dep.var.labels=c("","","","","","","")) ),
             glue("Results/Regressions/{cat_}_author.tex"))
}

# Author CV
for(cat_ in append(f1000_cat,"nb_cit")){
  mod_author_1 <- glm(substitute(i ~ author_intra_title + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_2 <- glm(substitute(i ~ author_inter_title + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_3 <- glm(substitute(i ~ author_intra_title + author_inter_title + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_4 <- glm(substitute(i ~ author_intra_abstract + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_5 <- glm(substitute(i ~ author_inter_abstract + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_6 <- glm(substitute(i ~ author_intra_abstract + author_inter_abstract + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_7 <- glm(substitute(i ~ author_intra_title + author_inter_title + author_intra_abstract + author_inter_abstract + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  
  
  l = list(mod_author_1, mod_author_2, mod_author_3, mod_author_4, mod_author_5,
           mod_author_6,mod_author_7)
  model_names = as.character(c(1:length((l))))
  writeLines(capture.output(stargazer(l,keep.stat = c("n", "rsq"),
                                      omit=append(variables ,c("Constant")),
                                      column.labels=c(cat_),
                                      dep.var.labels=c("","","","","","","")) ),
             glue("Results/Regressions/{cat_}_author_CV.tex"))
}

# Poisson field weighted ####

##### No CV 

for(cat_ in append(f1000_cat,"nb_cit")){
  mod_wang_1 <- glm(substitute(i ~ wang_mesh_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_wang_2 <- glm(substitute(i ~ wang_ref_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_wang_3 <- glm(substitute(i ~ wang_mesh_fw + wang_ref_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_1 <- glm(substitute(i ~ uzzi_mesh_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_2 <- glm(substitute(i ~ uzzi_ref_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_3 <- glm(substitute(i ~ uzzi_mesh_fw + uzzi_ref_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_1 <- glm(substitute(i ~ lee_mesh_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_2 <- glm(substitute(i ~ lee_ref_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_3 <- glm(substitute(i ~ lee_mesh_fw + lee_ref_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_1 <- glm(substitute(i ~ foster_mesh_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_2 <- glm(substitute(i ~ foster_ref_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_3 <- glm(substitute(i ~ foster_mesh_fw + foster_ref + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_1 <- glm(substitute(i ~ shibayama_abstract_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_2 <- glm(substitute(i ~ shibayama_title_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_3 <- glm(substitute(i ~ shibayama_abstract_fw + shibayama_title_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  
  l = list(mod_wang_1, mod_wang_2, mod_wang_3, mod_uzzi_1, mod_uzzi_2, mod_uzzi_3,
           mod_lee_1, mod_lee_2, mod_lee_3, mod_foster_1, mod_foster_2, mod_foster_3,
           mod_shib_1,mod_shib_2,mod_shib_3
  )
  
  writeLines(capture.output(stargazer(l, font.size = "small", keep.stat = c("n", "rsq"),
                                      omit=append(variables ,c("Constant")),
                                      column.labels=c(cat_),
                                      dep.var.labels=c("","","","","","","","","","","","","","",""),
                                      model.names=FALSE,
                                      no.space=TRUE) ),
             glue("Results/Regressions/{cat_}_fw.tex"))
}


# CV

for(cat_ in append(f1000_cat,"nb_cit")){
  mod_wang_1 <- glm(substitute(i ~ wang_mesh_fw + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_wang_2 <- glm(substitute(i ~ wang_ref_fw + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_wang_3 <- glm(substitute(i ~ wang_ref_fw + wang_mesh_fw + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_1 <- glm(substitute(i ~ uzzi_mesh_fw+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_2 <- glm(substitute(i ~ uzzi_ref_fw+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_uzzi_3 <- glm(substitute(i ~ uzzi_ref_fw + uzzi_mesh_fw+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_1 <- glm(substitute(i ~ lee_mesh_fw+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_2 <- glm(substitute(i ~ lee_ref_fw+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_lee_3 <- glm(substitute(i ~ lee_mesh_fw + lee_ref_fw+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_1 <- glm(substitute(i ~ foster_mesh_fw+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_2 <- glm(substitute(i ~ foster_ref_fw+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_foster_3 <- glm(substitute(i ~ foster_mesh_fw + foster_ref+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_1 <- glm(substitute(i ~ shibayama_abstract_fw+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_2 <- glm(substitute(i ~ shibayama_title_fw+ nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_shib_3 <- glm(substitute(i ~ shibayama_abstract_fw + shibayama_title_fw + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  
  l = list(mod_wang_1, mod_wang_2, mod_wang_3, mod_uzzi_1, mod_uzzi_2, mod_uzzi_3,
           mod_lee_1, mod_lee_2, mod_lee_3, mod_foster_1, mod_foster_2, mod_foster_3,
           mod_shib_1,mod_shib_2,mod_shib_3
  )
  
  writeLines(capture.output(stargazer(l, font.size = "small", keep.stat = c("n", "rsq"),
                                      omit=append(variables ,c("Constant")),
                                      column.labels=c(cat_),
                                      dep.var.labels=c("","","","","","","","","","","","","","",""),
                                      model.names=FALSE,
                                      no.space=TRUE) ),
             glue("Results/Regressions/{cat_}_CV_fw.tex"))
}

# Author no CV

for(cat_ in append(f1000_cat,"nb_cit")){
  mod_author_1 <- glm(substitute(i ~ author_intra_title_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_2 <- glm(substitute(i ~ author_inter_title_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_3 <- glm(substitute(i ~ author_intra_title_fw + author_inter_title_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_4 <- glm(substitute(i ~ author_intra_abstract_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_5 <- glm(substitute(i ~ author_inter_abstract_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_6 <- glm(substitute(i ~ author_intra_abstract_fw + author_inter_abstract_fw + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_7 <- glm(substitute(i ~ author_intra_title_fw + author_inter_title_fw + author_intra_abstract + author_inter_abstract + year, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  
  
  l = list(mod_author_1, mod_author_2, mod_author_3, mod_author_4, mod_author_5,
           mod_author_6,mod_author_7)
  model_names = as.character(c(1:length((l))))
  writeLines(capture.output(stargazer(l,keep.stat = c("n", "rsq"),
                                      omit=append(variables ,c("Constant")),
                                      column.labels=c(cat_),
                                      dep.var.labels=c("","","","","","","")) ),
             glue("Results/Regressions/{cat_}_author_fw.tex"))
}

# Author CV
for(cat_ in append(f1000_cat,"nb_cit")){
  mod_author_1 <- glm(substitute(i ~ author_intra_title_fw + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_2 <- glm(substitute(i ~ author_inter_title_fw + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_3 <- glm(substitute(i ~ author_intra_title_fw + author_inter_title_fw + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_4 <- glm(substitute(i ~ author_intra_abstract_fw + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_5 <- glm(substitute(i ~ author_inter_abstract_fw + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_6 <- glm(substitute(i ~ author_intra_abstract_fw + author_inter_abstract_fw + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  mod_author_7 <- glm(substitute(i ~ author_intra_title_fw + author_inter_title_fw + author_intra_abstract_fw + author_inter_abstract_fw + nb_ref + year + nb_aut + journal_SJR+journal_age, list(i = as.name(cat_))), data = df_f1000, family ="poisson")
  
  
  l = list(mod_author_1, mod_author_2, mod_author_3, mod_author_4, mod_author_5,
           mod_author_6,mod_author_7)
  model_names = as.character(c(1:length((l))))
  writeLines(capture.output(stargazer(l,keep.stat = c("n", "rsq"),
                                      omit=append(variables ,c("Constant")),
                                      column.labels=c(cat_),
                                      dep.var.labels=c("","","","","","","")) ),
             glue("Results/Regressions/{cat_}_author_CV_fw.tex"))
}

# Predict impact measure


