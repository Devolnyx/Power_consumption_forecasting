import numpy as np
import yaml
import pandas as pd
import tensorflow as tf

config_path = "./config/config.yaml"
config = yaml.safe_load(open(config_path))


def main(config):

    model_config = config['models']['onestep']
    data_config = config['resources']['onestep']

    df = pd.read_csv(data_config['path'])
    model = tf.keras.models.load_model(model_config['path'])
    data_pred = df[df.value.isna()][:1]
    df = df.dropna()

    def predict(df, model):
        X = df.drop(['dt', 'value'], axis=1).to_numpy()
        preds = model.predict(X).squeeze()
        return preds

    if len(data_pred) > 0:
        preds = predict(data_pred, model)
        data_pred['value'] = preds
        df = pd.concat([df[['dt', 'value']][-1:], data_pred])
        df.to_csv(data_config['pred'], index=False)

    else:
        pass

if __name__ == "__main__":
    main(config)