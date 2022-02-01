Create 2 folders to store the locally for jupyter and jupyter-pyspark
```sh
mkdir data && mkdir data/jupyter && mkdir data/jupyter-pyspark
```
Command to run Jupyter-nb
```sh
docker-compose -f docker-compose-jupyter.yml up
```

Command to run Jupyter-pyspark-nb
```sh
docker-compose -f docker-compose-jupyter-pyspark.yml up
```