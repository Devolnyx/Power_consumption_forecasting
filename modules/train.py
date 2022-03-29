import yaml
import tensorflow as tf


def retrain(X, y, model, config, mode='onestep'):

    if mode not in ['onestep', 'multistep']:
        raise Exception('Wrong mode specified')

    model_config = config['models'][mode]
    test_size = model_config['test_size']
    epochs = model_config['epochs']
    stop_rounds = model_config['early_stop']

    size = int(len(X)*test_size)
    X_train, y_train = X[-size:], y[-size:]
    X_test, y_test = X[:-size], y[:-size]

    estop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=stop_rounds,
                                             verbose=0, mode='min', restore_best_weights=True)

    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=epochs, callbacks=[estop], verbose=0)

    return model
