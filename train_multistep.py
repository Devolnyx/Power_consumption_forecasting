import yaml
import os
import tensorflow as tf
from modules.load_data import get_data
from modules.train import retrain

base_path = os.path.dirname(os.path.abspath(__file__))
print(base_path)

try:
    project_path = os.path.abspath(os.path.curdir)
    config_path = "/config/config.yaml"
    config = yaml.safe_load(open(project_path + config_path))
except:
    config = yaml.safe_load(open("/opt/airflow/config/config_airflow.yaml"))

def main(config):

    model_config = config['models']['multistep']
    data_config = config['resources']['multistep']

    df = get_data(config, mode='multistep')
    df.to_csv(data_config['path'], index=False)
    model = tf.keras.models.load_model(model_config['path'])

    target_cols = [x for x in df.columns if 'target_' in x]
    feature_cols = [x for x in df.columns if 'target_' not in x]

    def evaluate(df, model):
        df = df.dropna()[-48*7:]
        X = df[feature_cols].drop(['dt', 'value'], axis=1).to_numpy()
        y = df[target_cols].to_numpy()
        preds = model.predict(X).squeeze()
        return (abs(preds - y)).mean()

    def train(df, model, config):
        df = df.dropna()[-48 * 28:]
        X = df[feature_cols].drop(['dt', 'value'], axis=1).to_numpy()
        y = df[target_cols].to_numpy()
        model = retrain(X, y, model, config, mode="multistep")
        return model

    eval_score = evaluate(df, model)

    if eval_score > model_config['mae_threshold']:
        model = train(df, model, config)
        new_score = evaluate(df, model)

        if new_score < eval_score:
            model.save(model_config['path'])

    else:
        pass

if __name__ == "__main__":
    main(config)
