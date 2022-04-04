## Office power consumption forecasting

A scratch of a models and dashboard for monitoring and forecasting office power consumption.
 - Real data from the power meter received via API from the SEDMAX demo server;
 - The pipelines for requesting, loading, transform data, evaluating and training the model are built on Airflow;
 - The Dash module is used to visualize timeseries.

![изображение](https://user-images.githubusercontent.com/86562899/161625447-e1e7b606-fd99-4f10-9198-59d5ef9eb7c3.png)

## Docker Compose

The project uses the default Airflow docker-compose.yaml file with some modifications. Port 8080 exposed for Airflow, 8050 for Dash.
Build the images:

```sh
docker-compose up -d
```

## Run in local virtual enviroment

Use Airflow Standalone and run app.py
