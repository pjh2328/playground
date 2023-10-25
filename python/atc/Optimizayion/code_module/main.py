# main.py
from tensorflow import keras
import numpy as np
import tempfile
import os
import zipfile
import tensorflow as tf
import tensorflow_model_optimization as tfmot
from pruning_module import prune_model, export_pruned_model
from quantization_module import quantize_model

# 모델 크기 계산 함수
def get_gzipped_model_size(file):
    _, zipped_file = tempfile.mkstemp('.zip')
    with zipfile.ZipFile(zipped_file, 'w', compression=zipfile.ZIP_DEFLATED) as f:
        f.write(file)
    return os.path.getsize(zipped_file)

# 데이터 로드
mnist = keras.datasets.mnist
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
train_images = train_images / 255.0
test_images = test_images / 255.0
model = tf.keras.models.load_model("my_model.h5")
_, accuracy = model.evaluate(
   test_images, test_labels, verbose=0)

# 모델 가중치 가지치기 수행
model_for_pruning, model_for_pruning_accuracy = prune_model(model, train_images, train_labels, test_images, test_labels)
model_for_export = export_pruned_model(model_for_pruning)

# 가중치 가지치기 적용 모델 저장
model_for_pruning.save("pruned_model.h5")

# 모델 양자화 수행
q_aware_model, q_aware_model_accuracy = quantize_model(model, train_images, train_labels, test_images, test_labels)

# 양자화 적용 모델 저장
q_aware_model.save("quantized_model.h5")

# 나머지 코드 (크기 및 정확도 측정)는 그대로 사용합니다.
# 기능 매트릭 정리 
# 파일 크기를 정수로 변환하여 출력
keras_file_size = int(get_gzipped_model_size("my_model.h5"))
pruned_keras_file_size = int(get_gzipped_model_size("purned_model.h5"))
quant_file_size = int(get_gzipped_model_size("quantized_model.h5"))
# 압축률 = (압축 전 데이터 크기) / (압축 후 데이터 크기)
pruned_keras_compression_rate = (keras_file_size - (keras_file_size - pruned_keras_file_size)) / keras_file_size * 100
quant_file_compression_rate = (keras_file_size - (keras_file_size - quant_file_size)) / keras_file_size * 100
pruned_keras_compression_rate = "{:.2f}".format(pruned_keras_compression_rate)
quant_file_compression_rate = "{:.2f}".format(quant_file_compression_rate)
# 원본 모델 비교
PADP = (accuracy - (accuracy - model_for_pruning_accuracy)) / accuracy * 100
if PADP >= 100:
    PADP = 100
P = "{:.2f}".format(PADP)
PADQ = (accuracy - (accuracy - q_aware_model_accuracy)) / accuracy * 100
if PADQ >= 100:
    PADQ = 100
Q = "{:.2f}".format(PADQ)

# 각 모델간(원본, 가중치 가지치기, 양자화) 성능비교 매트릭 출력
print('모델 사이즈---------------------------------------------------')
print("Size of gzipped baseline Keras model: %d bytes" % keras_file_size)
print("Size of gzipped pruned Keras model: %d bytes" % pruned_keras_file_size)
print("Size of gzipped Quantized model: %d bytes" % quant_file_size)
print('모델 압축률---------------------------------------------------')
print("compression rate of pruned Keras model: ", pruned_keras_compression_rate,'%')
print("compression rate of Quantized model: ", quant_file_compression_rate,'%')
print('모델 최적화 성능----------------------------------------------')
print('Baseline test accuracy:', accuracy)
print('Pruned test accuracy:', model_for_pruning_accuracy)
print('Quant test accuracy:', q_aware_model_accuracy)
print('모델 최적화 비교 정확도----------------------------------------')
print('가지치기 비교 정확도 :', P,"%")
print('양자화 비교 정확도 :', Q,"%")