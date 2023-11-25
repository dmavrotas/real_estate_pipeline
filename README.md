# Real Estate Pipeline

## Premise 

This is an example of how we could integrate some real estate data to a data pipeline given some specific criteria.
This exercise aims to demonstrate how we handle a typical dataset through a very simplistic treatment.

## Code

There is a code demonstration that reads a sample file called `sample.json` which is read by a python script `real_estate_pipeline/main.py`. The result of the script is a csv file with the requested data, properly cleaned and formatted.

How to run the code example locally. The python script uses `poetry` to handle dependencies.

```
poetry shell
poetry install
python -m real_estate_pipeline.main

or

docker build -t <name> .
docker run <name>
```

## ETL Design & Implementation

As you can see from the example code in `real_estate_pipeline/main.py` we can identify some basic steps:
* Cleaning of the dataset (function `clean_dataset`) and then remove the invalid lines (`dropna`)
* Normalization of the dataset (function `normalize_dataset`), which will make sure our dataset can be queried the way we want and the values are relevant with our business. 
* Apply filters (function `filter_dataset`) and prepare dataset to be sent (function `prepare_dataset_for_send`).

To make things more visual, we could describe our ETL with the following schema:

![basic_etl_diagram.drawio.png](diagrams%2Fbasic_etl_diagram.drawio.png)

## Tools & Technologies

First of all, the language. Python is a very powerful scripting language with many useful languages and powerful frameworks.

We will be using poetry as our dependency manager, as it's efficient and can be easily installed in any machine.

We will be using docker for our containerization. 

For unit testing, we will be using `pytest`.

In the code example we are using Pandas, which is a simple, yet powerful tool. Had we been in a production environment we would probably use Spark, through the `pyspark` library. Why Spark ? Spark is a very popular tool that is widely for many use cases, it has a very easy-to-use SQL-like syntax and it can easily scale through Kubernetes in case we need more workers.

In the code example we are saving the data to a csv file in our filesystem. Had we been in a production environment, we would need to think more about our choice. The cheapest solution would be to save our files inside a datalake (something like a GCS, ABS or S3 bucket), in order to be cost-effective and have many options to manipulate our data. One of these options would be to use a technology like Apache Hudi or Iceberg. If we need to manipulate this dataset further so that it can also have more info such as geolocation (in order to be show on a map) we would need to use a database such as PSQL, MongoDB or BigQuery. All these 3 databases provide geospatial capabilities out-of-the-box, each one with its own drawbacks. PSQL seems to be quite popular due to its relatively low maintenance fees and versatility, providing some noSQL (key-value) capabilities. BigQuery is a database managed by Google which is gaining a lot of traction but while it does not need any maintenance, it is relatively expensive to run as it has a pay-as-you-go model.

If we need to be able to help our Data Science team safely query and discover our dataset, we have a good amount of choices. If we use Hudi or Iceberg, DataHub could be a good choice, since it has a good community and can connect to many data lake engines. If we are using a database such as BigQuery or PSQL we could use Tableau, which is a very powerful (albeit expensive) tool. 

## Output format

It all depends on the choice we made in the previous section. 

If we go with a data lake approach, our best bet would be to save in parquet format since it is very efficient and can save us a lot of space. On the other hand, we could use JSON if we would like to be able to easily import our data lake data in a database like MongoDB. 

If we go with a database approach, then our best bet is to adopt a JSON format, since it's supported by PSQL and BigQuery. One of the perks of JSON is that we can easily use technologies such as JSON Schema to validate our data structure. We could also use protobuf, but it's not officially supported.  

## Scalability & high traffic

What happens to the above sections if we have to support billions of data ? Our main pain points here would be :
* Our Spark cluster : There are 2 choices. Fiest, the out-of-the box Spark solution provided by cloud providers which is good for 90% of the cases and scales well based on demand. Its main disadvantage is that usually it takes time to support new versions and the scaling is usually expensive. The other one is to have our own Kubernetes Spark cluster. With KUbernetes we can control the cost and the way we want to upscale our resources, but we also need to have people that will take care of its maintenance and constant evolution. This could be mitigated if we use a serverless provisioning solution like `Fargate for EKS`.
* Our Storage: If we use a data lake, then our only concern will be to make sure that we have correct TTLs for our data to keep track of the cost, have correct indexes in order to achieve high compaction and reduce costs and of course, make sure that the extra load won't affect the performance of our queries. In case we're using a database, we will need to also take care of our TTLs, make sure we use the right indexes and make sure we have set up a correct HPA strategy (based on CPU + RAM consumption). Of course, that won't be a concern if our database is managed by our cloud provider.
* Our network capabilities: If we are going to scrap these data, we will need to make sure we have enough IPs at our disposal that will rotate on a regular basis. We also make sure that we're utilizing a proper strategy to spawn machines in different regions to reduce extra region-to-region costs as well as latency. 

## Extra steps

We could imagine a more refined cleaning step. We have mainly 2 cases that could be interesting for us.
* The data we reject from external sources would be interesting to be put against a Machine Learning model that will try to make sense and normalize them. We could use these data as less qualified sources later.
* The data we reject from in-house sources should be kept in a different place in order to be checked by our QA team since they don't respect our Schema Registry and therefore, we can easily catch breaking changes in our models.

Our architecture then would look like this : 

![basic_etl_diagram-extra-steps-case.drawio.png](diagrams%2Fbasic_etl_diagram-extra-steps-case.drawio.png)


