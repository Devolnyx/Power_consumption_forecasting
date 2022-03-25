import tensorflow as tf

def retrain(X,y,model, test_size = 0.33):
    size = int(len(X)*test_size)
    X_train, y_train = X[-size:], y[-size:]
    X_test, y_test = X[:-size], y[:-size]

    estop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=25,
                                             verbose=0, mode='min', restore_best_weights=True)

    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=300, callbacks=[estop], verbose=0)

    return model
