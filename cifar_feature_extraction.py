from keras.applications.resnet50 import ResNet50
from keras.applications.inception_v3 import InceptionV3
from keras.applications.vgg16 import VGG16
from keras.layers import Dense, Flatten, Input
from sklearn.model_selection import train_test_split
from keras.models import Model
from keras.datasets import cifar10
from skimage.transform import resize
import numpy as np

nb_classes = 10
batch_size = 32
nb_epoch = 5

(X_train, y_train), (X_test, y_test) = cifar10.load_data()

X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=0)
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_val = X_val.astype('float32')
X_train /= 255
X_test /= 255
X_val /= 255

def gen(data, labels, size=(224, 224)):
    def _f():
        start = 0
        end = start + batch_size
        n = data.shape[0]
        while True:
            X_batch_old, y_batch = data[start:end], labels[start:end]
            X_batch = []
            for i in range(X_batch_old.shape[0]):
                img = resize(X_batch_old[i, ...], size)
                X_batch.append(img)

            X_batch = np.array(X_batch)
            start += batch_size
            end += batch_size
            if start >= n:
                start = 0
                end = batch_size

            yield (X_batch, y_batch)
    return _f

input_tensor = Input(shape=(224, 224, 3))
# base_model = ResNet50(input_tensor=input_tensor, include_top=False)
# base_model = InceptionV3(input_tensor=input_tensor, include_top=False)
base_model = VGG16(input_tensor=input_tensor, include_top=False)

x = base_model.output
x = Flatten()(x)
x = Dense(512, activation='relu')(x)
x = Dense(nb_classes, activation='softmax')(x)
model = Model(base_model.input, x)

# freeze base model layers
for layer in base_model.layers:
    layer.trainable = False

model.compile(optimizer='sgd', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

train_gen = gen(X_train, y_train)
val_gen = gen(X_val, y_val)
model.fit_generator(
    train_gen(),
    X_train.shape[0],
    nb_epoch,
    nb_val_samples=X_val.shape[0],
    validation_data=val_gen())

_, acc = model.evaluate(X_test, y_test, verbose=0)
print("Testing accuracy =", acc)