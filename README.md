# PyTorch MNIST digit recognition
Итоговый проект курса "Машинное обучение в бизнесе"

Стек:

ML: pytorch, numpy
API: flask
Virtualization: docker

Данные: http://yann.lecun.com/exdb/mnist/ - MNIST датасет рукописных цифр

Задача: Мультиклассовая классификация (распознавание изображения).

Преобразование входного изображения:

- Resize - изменяем размер изображения до 32х32
- CenterCrop - обрезаем края вокруг центра до результирующего размер 28х28
- Grayscale - переводим в оттенки серого
- Negative - инвертируем
- ToTensor - преобразуем в тензор
- Normalize - нормируем со средним 0.5 и std 0.5

Так как модель была обучена на инвертированых изображениях, то изначальное
входное изображение должно быть черной (или цветной) цифрой на белом фоне.
В противном случае работает некорректно.

Модель:

Линейная(dense) сеть:

- 784 входных нейронов (28х28)
- 512 нейронов (dense)
- 256 нейронов (dense)
- 128 нейронов (dense)
- 10 выходных нейронов (10 классов цифр от 0 до 9)

50 эпох обучения (оптимизатор SGD, learning rate=0.003, momentum=0.9)
Training loss: 0.00049
Количество изображений валидационного датасета: 10000
Model accuracy: 0.9804

### Клонируем репозиторий и создаем образ
```
$ git clone https://github.com/dTenebrae/ds_in_business_project.git
$ cd ds_in_business_project
$ docker build -t mnist_rec .
```

### Запускаем контейнер
```
$ docker run -d -p 5000:5000 mnist_rec
```

### Переходим на localhost:5000

![alt text](https://github.com/dTenebrae/ds_in_business_project/blob/main/mnist_rec.jpg?raw=true)
