import tempfile
import os
import zipfile
import tensorflow as tf
import tensorflow_model_optimization as tfmot
import numpy as np
from tensorflow import keras

def get_gzipped_model_size(file):
    _, zipped_file = tempfile.mkstemp('.zip')
    with zipfile.ZipFile(zipped_file, 'w', compression=zipfile.ZIP_DEFLATED) as f:
        f.write(file)
    return os.path.getsize(zipped_file)

def load_and_evaluate_model(model_path, test_images, test_labels):
    model = tf.keras.models.load_model(model_path)
    _, accuracy = model.evaluate(test_images, test_labels, verbose=0)
    return accuracy

def prune_and_save_model(model, output_path, pruning_params, train_images, train_labels, batch_size, epochs, validation_split):
    num_images = train_images.shape[0] * (1 - validation_split)
    end_step = np.ceil(num_images / batch_size).astype(np.int32) * epochs
    pruning_params = {
    'pruning_schedule': tfmot.sparsity.keras.PolynomialDecay(
        initial_sparsity=0.50,
        final_sparsity=0.80,
        begin_step=0,
        end_step=end_step
    )}
    model_for_pruning = tfmot.sparsity.keras.prune_low_magnitude(model, **pruning_params)
    model_for_pruning.compile(optimizer='adam',
                              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                              metrics=['accuracy'])
    logdir = tempfile.mkdtemp()
    callbacks = [
        tfmot.sparsity.keras.UpdatePruningStep(),
        tfmot.sparsity.keras.PruningSummaries(log_dir=logdir),
    ]
    model_for_pruning.fit(train_images, train_labels, batch_size=batch_size, epochs=epochs,
                          validation_split=validation_split, callbacks=callbacks)
    model_for_pruning.save(output_path)

def quantize_and_save_model(model, output_path, train_images, train_labels, batch_size, epochs, validation_split):
    quantize_model = tfmot.quantization.keras.quantize_model
    q_aware_model = quantize_model(model)
    q_aware_model.compile(optimizer='adam',
                          loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                          metrics=['accuracy'])
    q_aware_model.fit(train_images, train_labels, batch_size=500, epochs=4, validation_split=0.1)
    q_aware_model.save(output_path)

def compute_metrics(model_paths, test_images, test_labels):
    metrics = {}
    for model_path in model_paths:
        accuracy = load_and_evaluate_model(model_path, test_images, test_labels)
        metrics[model_path] = accuracy
    return metrics

def compute_compression_rate(original_model_path, compressed_model_path):
    original_size = int(get_gzipped_model_size(original_model_path))
    compressed_size = int(get_gzipped_model_size(compressed_model_path))
    compression_rate = original_size / compressed_size
    return compression_rate
