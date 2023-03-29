# Cowswap Subgraph Query with DataStreams

There are two notebooks in this folder:
'''data_pipeline_final.ipynb''' - used to obtain on-chain historical data from subgraphs. the notebook will cache the dataset locally in a data folder.
Requirements:
    * >= Python 3.10
    * Subgrounds (pip install subgrounds)
    * Polars (pip install polars)

'''data_analysis.ipynb''' - used to analyze and produce charts for the report. Run this after the pipeline notebook to reproduce the charts.