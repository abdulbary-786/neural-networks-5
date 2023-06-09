# -*- coding: utf-8 -*-
"""лаб-ная работа №5 (искусственные нейронные сети).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1m10JMeLe7eeb8bfvMJvLhz5uJOMwQCpZ

# Задание 1. Использование предобученной модели

## 1.1. Выберите и импортируйте предобученную модель СНС для решения задач классификации из имеющихся в Keras: https://keras.io/api/applications/
"""

from google.colab import drive
drive.mount('/content/drive')

"""Import model MobileNet"""

from tensorflow.keras.applications.mobilenet import MobileNet
model = MobileNet(weights='imagenet')

"""## 1.2. Загрузите из сети Интернет 5 изображений с разными классами, из тех, что приведены в [списке](https://gist.github.com/yrevar/942d3a0ac09ec9e5eb3a), и сохраните их представление в список images"""

import os
from os import listdir
from os.path import isfile, join
import cv2

images = []

path = '/content/drive/MyDrive/work5/list'

onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

for i in onlyfiles:
  images.append(os.path.join(path, i))

"""## 1.3. Напишите функцию, принимающую на вход список с исходными изображениями и возвращающую список с преобразованными изображениями под формат входных данных выбранной Вами модели СНС.

(Не забудьте создать независимую копию исходного списка в теле функции, для обработки именно независимой копии, а не оригинального списка)
"""

from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet import preprocess_input, decode_predictions
import numpy as np

def function(images):
  cop = images.copy()
  result=[]
  for i in cop:
    img = image.load_img(i, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    result.append(x)
  return result

result = function(images)

"""## 1.4. Напишите функцию, принимающую на вход список с представлениями обработаннах изображений (результат работы функции из п. 1.3.) и возвращающую список предсказанных нейросетью классов. """

def function2(result):
  preds=[]
  for x in result:
    pred = model.predict(x)
    preds.append(decode_predictions(pred, top=1)[0])
  return preds

predictions = function2(result)

print(predictions)
print(predictions[0][0][1])

"""## 1.5. Выведите изображения и соответствующие им классы, вызывая соответствующие функции"""

from google.colab.patches import cv2_imshow
for index, path in enumerate(images):
  image = cv2.imread(path)
  output = image.copy()
  text = "{}: {:.2f}%".format(predictions[index][0][1], predictions[index][0][2] * 100)
  cv2.putText(output, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
	(0, 0, 255), 2)
  cv2_imshow(output)

"""# Задание 2. Использование обученной модели для работы со своим датасетом

## 2.1. Выберите и импортируйте предобученную модель СНС для решения задач классификации из имеющихся в Keras: https://keras.io/api/applications/
"""

from tensorflow.keras.applications.mobilenet import MobileNet
model = MobileNet(weights='imagenet')

"""## 2.2. Подготовка тренировочных данных. Разделение на обучающую и тестовую выборку"""

from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
import os
from imutils import paths
import random
import cv2
import time
import numpy as np
import json
import tensorflow as tf

data_dir = '/content/drive/MyDrive/Dataset'

img_height,img_width=224, 224
batch_size=32
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="validation",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

class_names = train_ds.class_names
print(class_names)

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 10))
for images, labels in train_ds.take(1):
  for i in range(3):
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(images[i].numpy().astype("uint8"))
    plt.title(class_names[labels[i]])
    plt.axis("on")

"""## 2.3. Обучение своей модели на основе предобученной модели mobilenet"""

base_model = tf.keras.applications.MobileNet(include_top=False, # убираем полносвязные слои
                   input_shape=(224, 224, 3), # меняем параметры входных данных на свои
                   pooling='avg', # значение параметра означает, что после последнего сверточного слоя будет применена операция среднего пулинга
                   weights='imagenet') # указываем используемые веса (путь к файлу с предобученными весами)

base_model.summary()

for layer in base_model.layers:
  layer.trainable=False

"""## 2.3. Создаем свою модель на основе mobilenet"""

from tensorflow.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam

my_model = Sequential()
my_model.add(base_model)
my_model.add(Flatten())
my_model.add(Dense(512, activation='relu'))
my_model.add(Dense(5, activation='softmax'))

my_model.summary()

optimizer = Adam(lr=0.001)
loss = 'sparse_categorical_crossentropy'
metrics=['accuracy']

my_model.compile(optimizer=optimizer,
                 loss= loss,
                 metrics=metrics)

epochs=10
history = my_model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs 
)

"""## 2.4. Визуализация процесса обучения модели"""

fig1 = plt.gcf()
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.axis(ymin=0.4,ymax=1)
plt.grid()
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epochs')
plt.legend(['train', 'validation'])
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.grid()
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.legend(['train', 'validation'])
plt.show()

"""## 2.5. Подготовьте набор проверочных данных см. Задание №1 (п. 1.2, 1.3, 1.4)"""

import os
from os import listdir
from os.path import isfile, join
import cv2

images = []

path = '/content/drive/MyDrive/work5/test'

onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

for i in onlyfiles:
  images.append(os.path.join(path, i))

from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet import preprocess_input, decode_predictions
import numpy as np

def function(images):
  cop = images.copy()
  result=[]
  for i in cop:
    img = image.load_img(i, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    result.append(x)
  return result

result = function(images)

def function2(result):
  preds=[]
  for x in result:
    pred = model.predict(x)
    preds.append(decode_predictions(pred, top=1)[0])
  return preds

predictions = function2(result)

"""## 2.6. Организуйте вывод изображений и соответствующих им классов"""

from google.colab.patches import cv2_imshow
for index, path in enumerate(images):
  image = cv2.imread(path)
  output = image.copy()
  text = "{}: {:.2f}%".format(predictions[index][0][1], predictions[index][0][2] * 100)
  cv2.putText(output, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
	(0, 0, 255), 2)
  cv2_imshow(output)