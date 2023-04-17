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

library(ks)

#setwd("G:/Github/Taxonomy-of-novelty")
#setwd("C:/Users/kevin/Documents/GitHub/Taxonomy-of-novelty")

#Author 90e percentil
#shiba
#issue with uzzi ref

df = fread('reg_df.csv')


# Simple correlation

assign_color <- function(variable) {
  if (variable %in% indicators_mesh) {
    return("blue")
  } else if (variable %in% indicators_ref) {
    return("red")
  } else if (variable %in% indicators_authors) {
    return("green")
  } else if (variable %in% dependant) {
    return("purple")
  }
}
library(RColorBrewer)
library(circlize)
indicators_mesh <- c("uzzi_mesh","lee_mesh","foster_mesh","wang_mesh")
indicators_ref<- c("uzzi_ref","lee_ref","foster_ref","wang_ref","shibayama_abstract","shibayama_title")
indicators_authors<- c("author_intra_abstract","author_inter_abstract",
                      "author_intra_title", "author_inter_title")
dependant <-  c("nb_cit","DI1","DI5","DI1nok","Breadth","Depth","DeIn")
all_variables <- c(indicators_mesh, indicators_ref, indicators_authors, dependant)
all_variables = paste0(all_variables,'_fw')
cor_matrix <- cor(df %>% dplyr::select(all_variables), use = "pairwise.complete.obs") 
colors <- sapply(all_variables, assign_color)

edge_list <- data.frame()

for (i in seq_along(all_variables)) {
  for (j in seq_along(all_variables)) {
    if (i < j) {
      edge_list <- rbind(edge_list, 
                         data.frame(Source = all_variables[i], 
                                    Target = all_variables[j], 
                                    Correlation = cor_matrix[i, j]))
    }
  }
}

edge_list = as.data.table(edge_list)[Correlation > 0.2 | Correlation < -0.2]


edge_list$col = ifelse(edge_list$Correlation>0,'blue','red')


chordDiagram(edge_list, grid.col = colors, col = edge_list$col, preAllocateTracks = list(track.height = 0.05),transparency = 0.2)


circos.clear()

res1 <- cor.mtest(df %>% dplyr::select(all_variables), conf.level = .95)

corrplot(cor_matrix,
         col = brewer.pal(n = 8, name = "PuOr"),
         tl.col = "black", tl.srt = 90)

corrplot(cor_matrix,title = "Correlation Plot",order="hclust", col = brewer.pal(n = 8, name = "PuOr"),
         addrect = 4, 
         tl.col = "black", tl.srt = 90)



library(ggjoy)
library(ggplot2)

df %<>% mutate(share_highly_explorative = ifelse(0 <= share_diverse & share_diverse  < 0.1,'0-10%',
                                            ifelse(0.1 <= share_diverse & share_diverse  < 0.2,'10%-20%',
                                                   ifelse(0.2 <=share_diverse & share_diverse  < 0.3,'20%-30%',
                                                          ifelse(0.3 <= share_diverse & share_diverse  < 0.4,'30%-40%',
                                                                 ifelse(0.4 <= share_diverse & share_diverse  < 0.5,'40%-50%',
                                                                        ifelse(0.5 <= share_diverse & share_diverse  < 0.6,'50%-60%',
                                                                               ifelse(0.6 <= share_diverse & share_diverse  < 0.7,'60%-70%',
                                                                                      ifelse(0.7 <= share_diverse & share_diverse  < 0.8,'70%-80%',
                                                                                             ifelse(0.8 <= share_diverse & share_diverse  < 0.9,'80%-90%','90%-100%')))))))))) 


dtf_nov = df %>% dplyr::select(share_highly_explorative, shibayama_abstract) %>% mutate(Variable = 'Novelty à la Lee (FW)')
colnames(dtf_nov)[2] = 'value'
dtf_cit = df %>% dplyr::select(share_highly_explorative, DI1nok) %>% mutate(Variable = 'Citaiton count (FW)')
colnames(dtf_cit)[2] = 'value'

dtf = rbind(dtf_cit,dtf_nov)

#Create data frame
set.seed(101)
dtf <- data.frame(variable = c(rnorm(1000),
                               rnorm(1000) + rep(1:10/2,each =100)),
                  group = rep(c("a","b"), each = 1000),
                  year = rep(2001:2010, each=100))

# Use ggplot2 and ggjoy packages  
ggplot(dtf,aes(x = value, y = as.factor(share_highly_explorative), fill = Variable)) +
  geom_joy(scale = 2,alpha = .5,rel_min_height = 0.01) + theme_minimal() 





# 1st scatter plot with smooth line - uzzi_ref vs author_inter_abstract_fw
p1 <- ggplot(df, aes(x = author_inter_abstract, y = log(uzzi_ref+1))) +
  geom_point(size = 0.1) +
  
  xlab("Cognitive distance") + ylab("TUzzi Ref") +theme_minimal()


# 2nd scatter plot with smooth line - lee_ref vs author_inter_abstract_fw
p2 <- ggplot(df, aes(x = author_inter_abstract, y = lee_ref)) +
  geom_point(size = 0.1) +
  xlab("Cognitive distance") + ylab("Lee Ref") +theme_minimal()

# 3rd scatter plot with smooth line - foster_ref vs author_inter_abstract
p3 <- ggplot(df, aes(x = author_inter_abstract, y = foster_ref)) +
  geom_point(size = 0.1) +
  
  xlab("Cognitive distance") + ylab("Foster Ref") +theme_minimal()

# 4th scatter plot with smooth line - wang_ref vs author_inter_abstract
p4 <- ggplot(df, aes(x = author_inter_abstract, y = log(wang_ref+1))) +
  geom_point(size = 0.1) +
  
  xlab("Cognitive distance") + ylab("Wang Ref") +theme_minimal()

# 5th scatter plot with smooth line - shibayama_abstract vs author_inter_abstract
p5 <- ggplot(df, aes(x = author_inter_abstract, y = shibayama_abstract)) +
  geom_point(size = 0.1) +
  
  xlab("Cognitive distance") + ylab("Shibayama Ref") +theme_minimal()

# Display the plots
require(grid)
require(gridExtra)
g <- arrangeGrob(p1,p2,p3,p4,p5, nrow=2) #generates g
ggsave(file="cog_on_nov.jpg", g) #saves g




# 1st scatter plot with smooth line - uzzi_ref vs author_inter_abstract
p1 <- ggplot(df, aes(x = author_inter_abstract, y = log(nb_cit+1))) +
  geom_point(size = 0.1) +
  
  xlab("Cognitive distance") + ylab("log(citation count +1)") +theme_minimal()


# 2nd scatter plot with smooth line - lee_ref vs author_inter_abstract
p2 <- ggplot(df, aes(x = author_inter_abstract, y = DI1)) +
  geom_point(size = 0.1) +
  
  xlab("Cognitive distance") + ylab("DI1") +theme_minimal()

# 3rd scatter plot with smooth line - foster_ref vs author_inter_abstract
p3 <- ggplot(df, aes(x = author_inter_abstract, y = DI5)) +
  geom_point(size = 0.1) +
  
  xlab("Cognitive distance") + ylab("DI5") +theme_minimal()

# 4th scatter plot with smooth line - wang_ref vs author_inter_abstract
p4 <- ggplot(df, aes(x = author_inter_abstract, y = DI1nok)) +
  geom_point(size = 0.1) +
  
  xlab("Cognitive distance") + ylab("DI1nok") +theme_minimal()

# 5th scatter plot with smooth line - shibayama_abstract vs author_inter_abstract
p5 <- ggplot(df, aes(x = author_inter_abstract, y = Depth)) +
  geom_point(size = 0.1) +
  
  xlab("Cognitive distance") + ylab("Depth") +theme_minimal()

# Display the plots
require(grid)
require(gridExtra)
g <- arrangeGrob(p1,p2,p3,p4,p5, nrow=2) #generates g
ggsave(file="cog_on_impact.jpg", g) #saves g

final_plt = gridExtra::grid.arrange(p1, p2, p3, p4, p5, ncol = 2, nrow = 3)











# 1st scatter plot with smooth line - uzzi_ref vs author_inter_abstract_fw
p1 <- ggplot(df, aes(x = share_diverse, y = log(uzzi_ref+1))) +
  geom_point(size = 0.1) +
  
  xlab("Share Highly Exploratory Profile") + ylab("Uzzi Ref") +theme_minimal()


# 2nd scatter plot with smooth line - lee_ref vs share_diverse_fw
p2 <- ggplot(df, aes(x = share_diverse, y = lee_ref)) +
  geom_point(size = 0.1) +
  xlab("Share Highly Exploratory Profile") + ylab("Lee Ref") +theme_minimal()

# 3rd scatter plot with smooth line - foster_ref vs share_diverse
p3 <- ggplot(df, aes(x = share_diverse, y = foster_ref)) +
  geom_point(size = 0.1) +
  
  xlab("Share Highly Exploratory Profile") + ylab("Foster Ref") +theme_minimal()

# 4th scatter plot with smooth line - wang_ref vs share_diverse
p4 <- ggplot(df, aes(x = share_diverse, y = log(wang_ref+1))) +
  geom_point(size = 0.1) +
  
  xlab("Share Highly Exploratory Profile") + ylab("Wang Ref") +theme_minimal()

# 5th scatter plot with smooth line - shibayama_abstract vs share_diverse
p5 <- ggplot(df, aes(x = share_diverse, y = shibayama_abstract)) +
  geom_point(size = 0.1) +
  
  xlab("Share Highly Exploratory Profile") + ylab("Shibayama Ref") +theme_minimal()

# Display the plots
require(grid)
require(gridExtra)
g <- arrangeGrob(p1,p2,p3,p4,p5, nrow=2) #generates g
ggsave(file="diverse_on_nov.jpg", g) #saves g




# 1st scatter plot with smooth line - uzzi_ref vs share_diverse
p1 <- ggplot(df, aes(x = share_diverse, y = log(nb_cit+1))) +
  geom_point(size = 0.1) +
  
  xlab("Share Highly Exploratory Profile") + ylab("log(citation count +1)") +theme_minimal()


# 2nd scatter plot with smooth line - lee_ref vs share_diverse
p2 <- ggplot(df, aes(x = share_diverse, y = DI1)) +
  geom_point(size = 0.1) +
  
  xlab("Share Highly Exploratory Profile") + ylab("DI1") +theme_minimal()

# 3rd scatter plot with smooth line - foster_ref vs share_diverse
p3 <- ggplot(df, aes(x = share_diverse, y = DI5)) +
  geom_point(size = 0.1) +
  
  xlab("Share Highly Exploratory Profile") + ylab("DI5") +theme_minimal()

# 4th scatter plot with smooth line - wang_ref vs share_diverse
p4 <- ggplot(df, aes(x = share_diverse, y = DI1nok)) +
  geom_point(size = 0.1) +
  
  xlab("Share Highly Exploratory Profile") + ylab("DI1nok") +theme_minimal()

# 5th scatter plot with smooth line - shibayama_abstract vs share_diverse
p5 <- ggplot(df, aes(x = share_diverse, y = Depth)) +
  geom_point(size = 0.1) +
  
  xlab("Share Highly Exploratory Profile") + ylab("Depth") +theme_minimal()

# Display the plots
require(grid)
require(gridExtra)
g <- arrangeGrob(p1,p2,p3,p4,p5, nrow=2) #generates g
ggsave(file="diverse_on_impact.jpg", g) #saves g












# 1st scatter plot with smooth line - uzzi_ref vs author_inter_abstract_fw
p1 <- ggplot(df, aes(x = author_intra_abstract, y = log(uzzi_ref+1))) +
  geom_point(size = 0.1) +
  
  xlab("Average Exploratory Profile") + ylab("Uzzi Ref") +theme_minimal()


# 2nd scatter plot with smooth line - lee_ref vs author_intra_abstract_fw
p2 <- ggplot(df, aes(x = author_intra_abstract, y = lee_ref)) +
  geom_point(size = 0.1) +
  xlab("Average Exploratory Profile") + ylab("Lee Ref") +theme_minimal()

# 3rd scatter plot with smooth line - foster_ref vs author_intra_abstract
p3 <- ggplot(df, aes(x = author_intra_abstract, y = foster_ref)) +
  geom_point(size = 0.1) +
  
  xlab("Average Exploratory Profile") + ylab("Foster Ref") +theme_minimal()

# 4th scatter plot with smooth line - wang_ref vs author_intra_abstract
p4 <- ggplot(df, aes(x = author_intra_abstract, y = log(wang_ref+1))) +
  geom_point(size = 0.1) +
  
  xlab("Average Exploratory Profile") + ylab("Wang Ref") +theme_minimal()

# 5th scatter plot with smooth line - shibayama_abstract vs author_intra_abstract
p5 <- ggplot(df, aes(x = author_intra_abstract, y = shibayama_abstract)) +
  geom_point(size = 0.1) +
  
  xlab("Average Exploratory Profile") + ylab("Shibayama Ref") +theme_minimal()

# Display the plots
require(grid)
require(gridExtra)
g <- arrangeGrob(p1,p2,p3,p4,p5, nrow=2) #generates g
ggsave(file="explo_on_nov.jpg", g) #saves g




# 1st scatter plot with smooth line - uzzi_ref vs author_intra_abstract
p1 <- ggplot(df, aes(x = author_intra_abstract, y = log(nb_cit+1))) +
  geom_point(size = 0.1) +
  
  xlab("Average Exploratory Profile") + ylab("log(citation count +1)") +theme_minimal()


# 2nd scatter plot with smooth line - lee_ref vs author_intra_abstract
p2 <- ggplot(df, aes(x = author_intra_abstract, y = DI1)) +
  geom_point(size = 0.1) +
  
  xlab("Average Exploratory Profile") + ylab("DI1") +theme_minimal()

# 3rd scatter plot with smooth line - foster_ref vs author_intra_abstract
p3 <- ggplot(df, aes(x = author_intra_abstract, y = DI5)) +
  geom_point(size = 0.1) +
  
  xlab("Average Exploratory Profile") + ylab("DI5") +theme_minimal()

# 4th scatter plot with smooth line - wang_ref vs author_intra_abstract
p4 <- ggplot(df, aes(x = author_intra_abstract, y = DI1nok)) +
  geom_point(size = 0.1) +
  
  xlab("Average Exploratory Profile") + ylab("DI1nok") +theme_minimal()

# 5th scatter plot with smooth line - shibayama_abstract vs author_intra_abstract
p5 <- ggplot(df, aes(x = author_intra_abstract, y = Depth)) +
  geom_point(size = 0.1) +
  
  xlab("Average Exploratory Profile") + ylab("Depth") +theme_minimal()

# Display the plots
require(grid)
require(gridExtra)
g <- arrangeGrob(p1,p2,p3,p4,p5, nrow=2) #generates g
ggsave(file="explo_on_impact.jpg", g) #saves g

final_plt = gridExtra::grid.arrange(p1, p2, p3, p4, p5, ncol = 2, nrow = 3)