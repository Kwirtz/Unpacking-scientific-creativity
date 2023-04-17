library(data.table)
library(dplyr)
library(mgcv)
library(MASS)
library(akima)
library(gridExtra)
library(plotly)

df = fread('reg_df.csv')

rotate <- function(x) t(apply(x, 2, rev))

plot3d = function(df,cog_var,nove_var,impact_var,colsca,z_title,y_title,plot_title){
  df_indicators = as_tibble(df) %>% filter(!is.na(get(cog_var)),
                                           !is.na(get(nove_var)),
                                           !is.na(get(impact_var))) %>% dplyr::select(cog_var,nove_var,impact_var)
  
  grid_df_indicators <- expand.grid(seq(min(df_indicators[,cog_var]), max(df_indicators[,cog_var]), length.out = 100),
                                    seq(min(df_indicators[,nove_var]), max(df_indicators[,nove_var]), length.out = 100))
  
  formula_ = paste0(impact_var,' ~ s(',cog_var,',',nove_var,', k = 10',')')
  colnames(grid_df_indicators) = c(cog_var,nove_var)
  model <- gam(as.formula(formula_), data = df_indicators)
  tmp_df = data.frame(v1 = grid_df_indicators[,cog_var],
                      v2 = grid_df_indicators[,nove_var])
  colnames(tmp_df) = c(cog_var,nove_var)
  grid_df_indicators[,'pred'] <- predict(model, newdata = tmp_df)
  colnames(grid_df_indicators)[which(colnames(grid_df_indicators)=='pred')] = impact_var
  
  z_matrix = matrix(grid_df_indicators[,impact_var], nrow = 100, ncol = 100, byrow = TRUE)
  #z_matrix[ rotate(upper.tri(z_matrix))] = NA
  
  
  surface_df_indicators <- list(x = ~seq(min(df_indicators[,cog_var]), max(df_indicators[,cog_var]), length.out = 100),
                                y = ~seq(min(df_indicators[,nove_var]), max(df_indicators[,nove_var]), length.out = 100),
                                z = ~z_matrix)
  
  team_title = ifelse(stringr::str_detect(cog_var,'inter'),"Team's ","Individual's ")
  nov_ind = stringr::str_to_title(strsplit(nove_var,'_')[[1]][1])
  nov_ent = ifelse(strsplit(nove_var,'_')[[1]][2] == 'ref','references',
                   ifelse(strsplit(nove_var,'_')[[1]][2] == 'mesh', 'mesh terms',' arbstract from the references'))
  x_title = paste0(team_title," cognitive diversty measured on abstracts (Field Weighted)")
  plot3d = plot_ly(x = ~seq(min(df_indicators[,cog_var]), max(df_indicators[,cog_var]), length.out = 100),
                   y = ~seq(min(df_indicators[,nove_var]), max(df_indicators[,nove_var]), length.out = 100),
                   z = ~z_matrix)%>%
    add_surface(opacity = 0.85,colorscale = list(c(0,"#ff7f0e" ),c(1, "#1f77b4"))) %>% 
    layout(scene = list(xaxis = list(title = x_title,
                                     titlefont = list(color=c('black'),family = 'Helvetica', size = 12)),
                        
                        yaxis = list(title = y_title,
                                     titlefont = list(color=c('black'),family = 'Helvetica', size = 12)),
                        
                        zaxis = list(title = z_title,
                                     titlefont = list(color=c('black'),family = 'Helvetica', size = 12)))) 
  htmlwidgets::saveWidget(plot3d,paste(c('3d',cog_var,nove_var,impact_var,'.html'),collapse = '_'))
  
  plot3d = plot_ly(x = ~seq(min(df_indicators[,cog_var]), max(df_indicators[,cog_var]), length.out = 100),
                   y = ~seq(min(df_indicators[,nove_var]), max(df_indicators[,nove_var]), length.out = 100),
                   z = ~z_matrix, type = "contour",colorscale = colsca )%>%
    layout(xaxis = list(title = x_title,
                        titlefont = list(color=c('black'),family = 'Helvetica', size = 12)),
           yaxis = list(title = y_title,
                        titlefont = list(color=c('black'),family = 'Helvetica', size = 12))) %>%
    colorbar(title =z_title)
  
  
  htmlwidgets::saveWidget(plot3d,paste(c('3d',cog_var,nove_var,impact_var,'contour.html'),collapse = '_'))
  return(plot3d)
}

#############################################
t = plot3d(df,
           cog_var = 'author_inter_abstract_fw',
           nove_var = 'author_intra_abstract_fw',
           impact_var = 'nb_aut',
           colsca = 'Reds',
           z_title = 'Team size',
           y_title = "Average exploratory profile in the team",
           plot_title = "Team size")

#for(imp in dependant){
p1 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'author_intra_abstract_fw',
            impact_var = 'nb_cit_fw',
            colsca = 'Greens',
            z_title = '# Citations (FW)',
            y_title = "Average exploratory profile in the team",
            plot_title = "Citations")
p2 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'author_intra_abstract_fw',
            impact_var = 'DI1nok_fw',
            colsca = 'Greens',
            z_title = 'DI1nok (FW)',
            y_title = "Average exploratory profile in the team",
            plot_title = "Disruption")
p3 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'author_intra_abstract_fw',
            impact_var = 'Depth_fw',
            colsca = 'Greens',
            z_title = 'Depth (FW)',
            y_title = "Average exploratory profile in the team",
            plot_title = "Depth")

p4 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'author_intra_abstract_fw',
            impact_var = 'lee_ref_fw',
            colsca = 'Blues',
            z_title = 'Lee (FW)',
            y_title = "Average exploratory profile in the team",
            plot_title = "Novelty (Lee)")
p6 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'author_intra_abstract_fw',
            impact_var = 'shibayama_abstract_fw',
            colsca = 'Blues',
            z_title = 'Shibayama (FW)',
            y_title = "Average exploratory profile in the team",
            plot_title = "Novelty (Shibayama)")
p5 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'author_intra_abstract_fw',
            impact_var = 'foster_ref_fw',
            colsca = 'Blues',
            z_title = 'Foster (FW)',
            y_title = "Average exploratory profile in the team",
            plot_title = "Novelty (Foster)")



impact = subplot(p1, p2, p3, p4, p5, p6, nrows = 2) %>%
  layout(
    yaxis = list(title = "Average exploratory profile in the team"),
    xaxis4 = list(title = "Team cognitive diversty (Abstract - FW)"),
    yaxis4 = list(title = "Average exploratory profile in the team"),
    xaxis5 = list(title = "Team cognitive diversty (Abstract - FW)"),
    xaxis6 = list(title = "Team cognitive diversty (Abstract - FW)"))



annotations = list( 
  list( 
    x = 0.05,  
    y = 1.0,  
    text = "Citations",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),  
  list( 
    x = 0.4,  
    y = 1,  
    text = "DI1nok",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),  
  list( 
    x = 0.74,  
    y = 1,  
    text = "Depth",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),
  list( 
    x = 0.05,  
    y = 0.48,  
    text = "Lee",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18)
  ),  
  list( 
    x = 0.4,  
    y = 0.48,  
    text = "Foster",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),  
  list( 
    x = 0.74,  
    y = 0.48,  
    text = "Shibayama",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ))


htmlwidgets::saveWidget(impact %>%layout(annotations = annotations),'intra_aut_cog.html')


p1 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'share_diverse',
            impact_var = 'nb_cit_fw',
            colsca = 'Greens',
            z_title = '# Citations (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Citations")
p2 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'share_diverse',
            impact_var = 'DI1nok_fw',
            colsca = 'Greens',
            z_title = 'DI1nok (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Disruption")
p3 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'share_diverse',
            impact_var = 'Depth_fw',
            colsca = 'Greens',
            z_title = 'Depth (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Depth")


p4 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'share_diverse',
            impact_var = 'lee_ref_fw',
            colsca = 'Blues',
            z_title = 'Lee (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Novelty (Lee)")
p6 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'share_diverse',
            impact_var = 'shibayama_abstract_fw',
            colsca = 'Blues',
            z_title = 'Shibayama (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Novelty (Shibayama)")
p5 = plot3d(df,
            cog_var = 'author_inter_abstract_fw',
            nove_var = 'share_diverse',
            impact_var = 'foster_ref_fw',
            colsca = 'Blues',
            z_title = 'Foster (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Novelty (Foster)")


nov = subplot(p1, p2, p3, p4, p5, p6, nrows = 2)  %>%
  layout(#title = "Cognitive dimension and Novelty (References)",
    yaxis = list(title = "Share highly exploratory profile in the team"),
    xaxis4 = list(title = "Team cognitive diversty (Abstract - FW)"),
    yaxis4 = list(title = "Share highly exploratory profile in the team"),
    xaxis5 = list(title = "Team cognitive diversty (Abstract - FW)"),
    xaxis6 = list(title = "Team cognitive diversty (Abstract - FW)"))

annotations = list( 
  list( 
    x = 0.05,  
    y = 1,  
    text = "Citations",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),  
  list( 
    x = 0.4,  
    y = 1,  
    text = "DI1nok",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),  
  list( 
    x = 0.74,  
    y = 1,  
    text = "Depth",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),
  list( 
    x = 0.05,  
    y = 0.48,  
    text = "Lee",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),  
  list( 
    x = 0.4,  
    y = 0.48,  
    text = "Foster",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),  
  list( 
    x = 0.74,  
    y = 0.48,  
    text = "Shibayama",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ))

htmlwidgets::saveWidget(nov %>%layout(annotations = annotations),'highly_cog.html')


############################################################


p1 = plot3d(df,
            cog_var = 'share_typical',
            nove_var = 'share_diverse',
            impact_var = 'nb_cit_fw',
            colsca = 'Greens',
            z_title = '# Citations (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Citations")
p2 = plot3d(df,
            cog_var = 'share_typical',
            nove_var = 'share_diverse',
            impact_var = 'DI1nok_fw',
            colsca = 'Greens',
            z_title = 'DI1nok (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Disruption")
p3 = plot3d(df,
            cog_var = 'share_typical',
            nove_var = 'share_diverse',
            impact_var = 'Depth_fw',
            colsca = 'Greens',
            z_title = 'Depth (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Depth")


p4 = plot3d(df,
            cog_var = 'share_typical',
            nove_var = 'share_diverse',
            impact_var = 'lee_ref_fw',
            colsca = 'Blues',
            z_title = 'Lee (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Novelty (Lee)")
p6 = plot3d(df,
            cog_var = 'share_typical',
            nove_var = 'share_diverse',
            impact_var = 'shibayama_abstract_fw',
            colsca = 'Blues',
            z_title = 'Shibayama (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Novelty (Shibayama)")
p5 = plot3d(df,
            cog_var = 'share_typical',
            nove_var = 'share_diverse',
            impact_var = 'foster_ref_fw',
            colsca = 'Blues',
            z_title = 'Foster (FW)',
            y_title = "Share highly exploratory profile in the team",
            plot_title = "Novelty (Foster)")


nov = subplot(p1, p2, p3, p4, p5, p6, nrows = 2)  %>%
  layout(#title = "Cognitive dimension and Novelty (References)",
    yaxis = list(title = "Share highly exploratory profile in the team"),
    xaxis4 = list(title = "Share of highly exploitative profile in the team"),
    yaxis4 = list(title = "Share highly exploratory profile in the team"),
    xaxis5 = list(title = "Share of highly exploitative profile in the team"),
    xaxis6 = list(title = "Share of highly exploitative profile in the team"))

annotations = list( 
  list( 
    x = 0.05,  
    y = 1,  
    text = "Citations",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),  
  list( 
    x = 0.4,  
    y = 1,  
    text = "DI1nok",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),  
  list( 
    x = 0.74,  
    y = 1,  
    text = "Depth",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),
  list( 
    x = 0.05,  
    y = 0.48,  
    text = "Lee",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),  
  list( 
    x = 0.4,  
    y = 0.48,  
    text = "Foster",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ),  
  list( 
    x = 0.74,  
    y = 0.48,  
    text = "Shibayama",  
    xref = "paper",  
    yref = "paper",  
    xanchor = "center",  
    yanchor = "bottom",  
    showarrow = FALSE ,     font = list(color = "A0522D",size=18) 
  ))

htmlwidgets::saveWidget(nov %>%layout(annotations = annotations),'highly_typic_cog.html')

saveRDS(df_f1000, file = "Data/regression_data.rds")

plot(data=df_f1000,x=nb_aut, y=author_intra_title_fw)

ggplot(data=df_f1000[df_f1000$nb_aut < 50, ] , aes(x=nb_aut, y=wang_ref)) + 
  geom_point()




z_matrix <- tryCatch(
  {
    x = as.numeric(as.matrix(df_indicators[,c(cog_var)]))
    y = as.numeric(as.matrix(df_indicators[,c(nove_var)]))
    densite <- kde2d(x, y, n = 100)
    quantile5 = quantile(as.vector(densite$z),0.20)
    z_matrix <- matrix(grid_df_indicators[,impact_var], nrow = 100, ncol = 100, byrow = TRUE)
    z_matrix[which(densite$z < quantile5)] = NA
    z_matrix
  }
  ,error=function(e){
    return(matrix(grid_df_indicators[,impact_var], nrow = 100, ncol = 100, byrow = TRUE))
  })