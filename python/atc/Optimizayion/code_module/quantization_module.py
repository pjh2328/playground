# quantization_module.py
import tensorflow as tf
import tensorflow_model_optimization as tfmot

def quantize_model(model, train_images, train_labels, test_images, test_labels):
    quantize_model = tfmot.quantization.keras.quantize_model
    q_aware_model = quantize_model(model)
    q_aware_model.compile(optimizer='adam',
                          loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                          metrics=['accuracy'])
    q_aware_model.fit(train_images, train_labels,
                      batch_size=500, epochs=4, validation_split=0.1)
    _, q_aware_model_accuracy = q_aware_model.evaluate(
        test_images, test_labels, verbose=0)
    return q_aware_model, q_aware_model_accuracy
