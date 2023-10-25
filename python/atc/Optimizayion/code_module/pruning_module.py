# pruning_module.py
import tensorflow as tf
import tensorflow_model_optimization as tfmot
import numpy as np
import tempfile

def prune_model(model, train_images, train_labels, test_images, test_labels):
    prune_low_magnitude = tfmot.sparsity.keras.prune_low_magnitude
    batch_size = 128
    epochs = 4
    validation_split = 0.1
    num_images = train_images.shape[0] * (1 - validation_split)
    end_step = np.ceil(num_images / batch_size).astype(np.int32) * epochs
    pruning_params = {
        'pruning_schedule': tfmot.sparsity.keras.PolynomialDecay(
            initial_sparsity=0.50,
            final_sparsity=0.80,
            begin_step=0,
            end_step=end_step)
    }
    model_for_pruning = prune_low_magnitude(model, **pruning_params)
    model_for_pruning.compile(optimizer='adam',
                              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                              metrics=['accuracy'])
    logdir = tempfile.mkdtemp()
    callbacks = [
        tfmot.sparsity.keras.UpdatePruningStep(),
        tfmot.sparsity.keras.PruningSummaries(log_dir=logdir),
    ]
    model_for_pruning.fit(train_images, train_labels,
                          batch_size=batch_size, epochs=epochs, validation_split=validation_split,
                          callbacks=callbacks)
    _, model_for_pruning_accuracy = model_for_pruning.evaluate(
        test_images, test_labels, verbose=0)
    return model_for_pruning, model_for_pruning_accuracy

def export_pruned_model(model):
    return tfmot.sparsity.keras.strip_pruning(model)
