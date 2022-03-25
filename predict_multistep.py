import numpy as np
import yaml
import pandas as pd
import tensorflow as tf

config_path = "./config/config.yaml"
config = yaml.safe_load(open(config_path))


def main(config):

    model_config = config['models']['multistep']
    data_config = config['resources']['multistep']

    df = pd.read_csv(data_config['path'])
    model = tf.keras.models.load_model(model_config['path'])
    df_pred = df[df.value.isna()][:1]
    df = df.dropna(subset='value')

    feature_cols = [x for x in df.columns if 'target_' not in x]

    def predict(df, model):

        X = df[feature_cols].drop(['dt', 'value'], axis=1).to_numpy()
        preds = model.predict(X).squeeze()
        return preds

    def build_frame(df, df_pred, predictions):
        data_pred = pd.to_timedelta(range(0, 30 * 48, 30), unit='m').to_frame() + pd.to_datetime(df_pred.dt).item()
        data_pred = data_pred.rename(columns={0: 'dt'})
        data_pred = data_pred.reset_index().drop('index', axis=1)
        data_pred['value'] = predictions.squeeze()
        data_pred = pd.concat([df[['dt', 'value']][-1:], data_pred])
        return data_pred

    if len(df_pred) > 0:
        preds = predict(df_pred, model)
        data = build_frame(df, df_pred, preds)
        data.to_csv(data_config['pred'], index=False)

    else:
        pass

if __name__ == "__main__":
    main(config)