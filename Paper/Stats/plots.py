import novelpy

doc_infos = novelpy.plot_dist(doc_id = 23255530,
                      doc_year = 2015,
                      variable = ["c04_referencelist"],
                      id_variable = "PMID",
                      indicator = ["foster","lee"],
                      )
doc_infos.get_plot_dist()
df = doc_infos.df


trend = novelpy.novelty_trend(year_range = range(2000,2016,1),
              variable = ["c04_referencelist","a06_meshheadinglist"],
              indicator = ["foster","commonness"],
              time_window_cooc = [3],
              n_reutilisation = [1])

trend.get_plot_trend()

corr = novelpy.correlation_indicators(year_range = range(2000,2016,1),
              variable = ["c04_referencelist","a06_meshheadinglist"],
              indicator = ["foster","commonness"],
              time_window_cooc = [3],
              n_reutilisation = [1])

corr.correlation_heatmap()
df = corr.corr
sns.heatmap(df[2014].corr())