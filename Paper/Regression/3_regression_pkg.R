### Generic preamble
rm(list = ls(all.names = TRUE)) #will clear all objects includes hidden objects.
gc() #free up memrory and report the memory usage.
graphics.off()

library(data.table)


reg = function(dependant,sq,int,fw,higly_exp = F){
    if(fw){
      dependant = paste0(dependant,'_fw')
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
      independant = 'author_inter_abstract + author_intra_abstract'
      independant_sq = 'I(author_inter_abstract**2) + I(author_intra_abstract**2)'
      independant_inter = 'I(author_inter_abstract*author_intra_abstract)'
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
               dependant)
    }
    
    tmp = na.omit(df[,..vars_])
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
      model = lm(formula = as.formula(formula_), tmp)
    
    vcov_cluster <- sandwich::vcovCL(model, cluster = tmp$Journal_ISSN)
  
    return(list(model,vcov_cluster))
}

get_table = function(all_dep,title,sq,int,fw,higly_exp=F){
 
  models = list()
  cov = list()
  for(i in 1:length(all_dep)){
    model = reg(dependant = all_dep[i],
                sq = sq,
                int = int,
                fw = fw,
                higly_exp = higly_exp)
    models[[i]] = model[[1]]
    cov[[i]] = sqrt(diag(model[[2]]))
  }
  if(sq){
    title = paste0(title,'_sq')
  }
  if(int){
    title = paste0(title,'_int')
  }
  stargazer::stargazer(
    models, 
    se = cov,
    align = TRUE, type = "latex",
    keep = c('author_inter_abstract','author_intra_abstract','share_diverse',
             "share_typical",'nb_aut','nb_ref','nb_meshterms','sum_deg_cen_cumsum','journal_SJR'),
    out = paste0(gsub(' ','_',title),'.tex')
    )
}

df = fread('reg_df.csv')

all_dep =  c("uzzi_ref","lee_ref","foster_ref","wang_ref","shibayama_abstract")


get_table(all_dep,
          'Cognitive dimension and Novelty (on References)',
          sq = F, 
          int = F,
          fw = F)

get_table(all_dep,
          'Cognitive dimension and Novelty (On References; Field-Year percentage rank)',
          sq = F, 
          int = F,
          fw = T)

all_dep =  c("uzzi_mesh","lee_mesh","foster_mesh","wang_mesh")

get_table(all_dep,
          'Cognitive dimension and Novelty (on Meshterms)',
          sq = F, 
          int = F,
          fw = F)

get_table(all_dep,
          'Cognitive dimension and Novelty (On Meshterms; Field-Year percentage rank)',
          sq = F, 
          int = F,
          fw = T)


all_dep =  c("nb_cit","DI1","DI5","DI1nok","DeIn","Breadth","Depth")

get_table(all_dep,
          'Cognitive dimension and Scientific Impact',
          sq = F, 
          int = F,
          fw = F)

get_table(all_dep,
          'Cognitive dimension and Scientific Impact (Field-Year percentage rank)',
          sq = F, 
          int = F,
          fw = T)





#-----------------------------------------------------------------------------



all_dep =  c("uzzi_ref","lee_ref","foster_ref","wang_ref","shibayama_abstract")


get_table(all_dep,
          'Cognitive diversity, Share of higly exploratory individuals and Novelty (on References)',
          sq = F, 
          int = F,
          fw = F,
          higly_exp = T)

get_table(all_dep,
          'Cognitive diversity, Share of higly exploratory individuals and Novelty (On References; Field-Year percentage rank)',
          sq = F, 
          int = F,
          fw = T,
          higly_exp = T)

all_dep =  c("uzzi_mesh","lee_mesh","foster_mesh","wang_mesh")

get_table(all_dep,
          'Cognitive diversity, Share of higly exploratory individuals and Novelty (on Meshterms)',
          sq = F, 
          int = F,
          fw = F,
          higly_exp = T)

get_table(all_dep,
          'Cognitive diversity, Share of higly exploratory individuals and Novelty (On Meshterms; Field-Year percentage rank)',
          sq = F, 
          int = F,
          fw = T,
          higly_exp = T)


all_dep =  c("nb_cit","DI1","DI5","DI1nok","DeIn","Breadth","Depth")

get_table(all_dep,
          'Cognitive diversity, Share of higly exploratory individuals and Scientific Impact',
          sq = F, 
          int = F,
          fw = F,
          higly_exp = T)

get_table(all_dep,
          'Cognitive diversity, Share of higly exploratory individuals and Scientific Impact (Field-Year percentage rank)',
          sq = F, 
          int = F,
          fw = T,
          higly_exp = T)
