import tensorflow as tf
import numpy as np
import tempfile
import tensorflow_model_optimization as tfmot


def prune_and_train_model(model, train_images, train_labels, test_images, test_labels, batch_size, epochs, validation_split):
    # 가중치 가지치기를 위한 파라미터 설정
    prune_low_magnitude = tfmot.sparsity.keras.prune_low_magnitude
    num_images = train_images.shape[0] * (1 - validation_split)
    end_step = np.ceil(num_images / batch_size).astype(np.int32) * epochs
    pruning_params = {
        'pruning_schedule': tfmot.sparsity.keras.PolynomialDecay(
            initial_sparsity=0.50,
            final_sparsity=0.80,
            begin_step=0,
            end_step=end_step
        )
    }
    
    # 가중치 가지치기 모델 생성
    model_for_pruning = prune_low_magnitude(model, **pruning_params)
    
    # 모델 컴파일
    model_for_pruning.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )
    
    # 로그 디렉토리 설정
    logdir = tempfile.mkdtemp()
    
    # 콜백 설정
    callbacks = [
        tfmot.sparsity.keras.UpdatePruningStep(),
        tfmot.sparsity.keras.PruningSummaries(log_dir=logdir)
    ]
    
    # 모델 훈련
    model_for_pruning.fit(
        train_images, train_labels,
        batch_size=batch_size, epochs=epochs,
        validation_split=validation_split,
        callbacks=callbacks
    )
    
    # 가중치 가지치기가 적용된 모델 평가
    _, model_for_pruning_accuracy = model_for_pruning.evaluate(test_images, test_labels, verbose=0)
    
    # 가중치 가지치기 적용 모델의 원본 모델 복원
    model_for_export = tfmot.sparsity.keras.strip_pruning(model_for_pruning)
    
    # 가중치 가지치기가 적용된 모델 요약 출력
    model_for_pruning.summary()
    
    return model_for_export, model_for_pruning_accuracy



import tensorflow as tf
import tensorflow_model_optimization as tfmot
from tensorflow import keras

def quantize_and_convert_model(model, train_images, train_labels, test_images, test_labels, batch_size, epochs, validation_split):
    # Quantize the model
    quantize_model = tfmot.quantization.keras.quantize_model
    q_aware_model = quantize_model(model)
    
    # Compile the quantized model
    q_aware_model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])
    
    # Train the quantized model
    q_aware_model.fit(train_images, train_labels,
                      batch_size=batch_size, epochs=epochs, validation_split=validation_split)
    
    # Evaluate the quantized model
    _, q_aware_model_accuracy = q_aware_model.evaluate(test_images, test_labels, verbose=0)
    
    # Convert the quantized model to TensorFlow Lite
    converter = tf.lite.TFLiteConverter.from_keras_model(q_aware_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    quantized_tflite_model = converter.convert()
    
    # Print the summary of the quantized model
    q_aware_model.summary()
    
    return quantized_tflite_model, q_aware_model_accuracy

# Example usage:
# quantized_tflite_model, q_aware_model_accuracy = quantize_and_convert_model(model, train_images, train_labels, test_images, test_labels, batch_size, epochs, validation_split)
