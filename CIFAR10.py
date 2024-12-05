# -*- coding: utf-8 -*-
"""computer_vision.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kFjMHwwy1z2z-4AlyC4AQU8kJIB14siE
"""

import torch
from torch import nn

# Import torchvision
import torchvision
from torchvision import datasets
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader


import matplotlib.pyplot as plt

import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
device

train_data  = datasets.FashionMNIST(
    root = "data",
    train = True,
    download = True,
    transform = ToTensor(),
    target_transform = None
)
test_data = datasets.FashionMNIST(
    root = "data",
    train = False,
    download = True,
    transform = ToTensor(),
    target_transform = None
)

torch.manual_seed(42)

plt.figure(figsize=(9,9))

rows, columns = 4,4

for i in range(1, rows*columns+1):
  random_idx = torch.randint(0,len(train_data),size=[1]).item()
  image, label =train_data[i]
  plt.subplot(rows,columns,i)
  plt.imshow(image.squeeze())
  plt.title(train_data.classes[label])
  plt.axis(False)

BATCH_SIZE = 32

train_DataLoader = DataLoader(train_data,batch_size = BATCH_SIZE, shuffle = True)

test_DataLoader = DataLoader(test_data, batch_size = BATCH_SIZE, shuffle = False)

train_features_batch,train_labels_batch = next(iter(train_DataLoader))
test_features_batch, test_labels_batch = next(iter(test_DataLoader))

class FashionModel(nn.Module):
  def __init__(self):
    super().__init__()
    self.layer1 = nn.Sequential(
        nn.Conv2d(in_channels = 1, out_channels=10, kernel_size=3, stride=1, padding=1),
        nn.ReLU(),
        nn.Conv2d(in_channels = 10, out_channels=10, kernel_size=3, stride=1, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2,stride=2)
    )
    self.layer2=nn.Sequential(
        nn.Conv2d(in_channels=10, out_channels=10, kernel_size=3, stride=1, padding=1),
        nn.ReLU(),
        nn.Conv2d(in_channels=10, out_channels=10, kernel_size=3, stride=1, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2,stride=2)
    )
    self.classifier = nn.Sequential(
        nn.Flatten(),
        nn.Linear(in_features=10*7*7, out_features =10)
    )

  def forward(self,x):
    x = self.layer1(x)
    x = self.layer2(x)
    x = self.classifier(x)
    return x
def accuracy(y_pred, y):
  correct = torch.eq(y_pred, y).sum().item()
  return (correct/len(y))*100

model = FashionModel().to(device)

loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(params = model.parameters(), lr=0.1)

from timeit import default_timer as timer

def print_train_time(start, end, device):
  time = end - start
  print(f"Train time on {device}: {time:.3f} seconds")
  return time

def eval_model(model, data_loader, loss_fn, accuracy_fn):
  model.eval()
  test_loss, test_acc = 0, 0
  for X, y in data_loader:
    X, y = X.to(next(model.parameters()).device), y.to(next(model.parameters()).device)
    y_pred = model(X)
    loss = loss_fn(y_pred, y)
    acc = accuracy_fn(y_pred.argmax(dim=1), y)
    test_loss += loss
    test_acc += acc
  test_loss /= len(data_loader)
  test_acc /= len(data_loader)
  print(f"Test loss: {test_loss:.5f} | Test accuracy: {test_acc:.2f}%\n")


def train_step(model, data_loader, loss_fn, optimizer, accuracy_fn):
  model.train()
  train_loss, train_acc = 0, 0

  for X, y in data_loader:
    X, y = X.to(next(model.parameters()).device), y.to(next(model.parameters()).device)
    y_pred = model(X)
    loss = loss_fn(y_pred, y)
    acc = accuracy_fn(y_pred.argmax(dim = 1),y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    train_loss += loss
    train_acc += acc
  train_loss /= len(data_loader)
  train_acc /= len(data_loader)
  print(f"Train loss: {train_loss:.5f} | Train accuracy: {train_acc:.2f}%")

torch.manual_seed(42)
epochs = 10

for epoch in range(epochs):
  train_step(model, train_DataLoader, loss_fn, optimizer, accuracy)

  eval_model(model, test_DataLoader, loss_fn, accuracy)