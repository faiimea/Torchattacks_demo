{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 111,
   "metadata": {},
   "outputs": [],
   "source": [
    "import torch\n",
    "import torch.nn as nn\n",
    "import torch.optim as optim\n",
    "import torchvision.transforms as transforms\n",
    "import torchvision.datasets as datasets\n",
    "from torch.utils.data import DataLoader\n",
    "from torch.nn import Sequential, Conv2d,MaxPool2d,Flatten,Linear\n",
    "import torchvision\n",
    "import cv2\n",
    "import numpy as np\n",
    "from PIL import Image\n",
    "import matplotlib.pyplot as plt\n",
    "import torch.nn.functional as F\n",
    "from torch.utils.data import Dataset,DataLoader\n",
    "import os"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 112,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 定义一些超参数，如批次大小、学习速率、训练时的迭代次数等\n",
    "batch_size = 32\n",
    "learning_rate = 0.001\n",
    "num_epochs = 10\n",
    "\n",
    "# 定义数据增强和预处理的transforms。\n",
    "# 我们使用了随机水平翻转、随机垂直翻转和随机裁剪等transforms，以增加数据集的多样性。\n",
    "train_transforms = transforms.Compose([\n",
    "    transforms.Resize(256),\n",
    "    transforms.RandomCrop(224),\n",
    "    transforms.RandomHorizontalFlip(),\n",
    "    transforms.RandomVerticalFlip(),\n",
    "    transforms.ToTensor(),\n",
    "    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])\n",
    "])\n",
    "\n",
    "test_transforms = transforms.Compose([\n",
    "    transforms.Resize(256),\n",
    "    transforms.CenterCrop(224),\n",
    "    transforms.ToTensor(),\n",
    "    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])\n",
    "])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 113,
   "metadata": {},
   "outputs": [],
   "source": [
    "#resnet网络\n",
    "class Net(nn.Module):\n",
    "    def __init__(self):\n",
    "        super(Net, self).__init__()\n",
    "        self.resnet = nn.Sequential(*list(torchvision.models.resnet50(pretrained=True).children())[:-1])\n",
    "        self.fc = nn.Linear(2048, 2)\n",
    "\n",
    "    def forward(self, x):\n",
    "        x = self.resnet(x)\n",
    "        x = x.view(x.size(0), -1)\n",
    "        x = self.fc(x)\n",
    "        return x\n",
    "    \n",
    "    def predict(self, x):\n",
    "        logits = self.forward(x)\n",
    "        return F.softmax(logits, dim=1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 114,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 加载数据集。\n",
    "# 我们使用ImageNet数据集中的训练集和验证集，每个图像大小为224x224。\n",
    "# 构建Dataset数据集\n",
    "class MyDataset(Dataset):#需要继承torch.utils.data.Dataset\n",
    "    def __init__(self,feature,target):\n",
    "        super(MyDataset, self).__init__()\n",
    "        self.feature =feature\n",
    "        self.target = target\n",
    "    def __getitem__(self,index):\n",
    "        item=self.feature[index]\n",
    "        label=self.target[index]\n",
    "        return item,label\n",
    "    def __len__(self):\n",
    "        return len(self.feature)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 115,
   "metadata": {},
   "outputs": [],
   "source": [
    "train_rate=0.8"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 在这里更改路径，以增加更多图片用来训练"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 数据集功能\n",
    "GRAY_img GRAY_FGSM_img 原灰度图像\n",
    "\n",
    "new_gray_img new_gray_fgsm_img 更改过顺序的全部灰度图像\n",
    "\n",
    "new_small_img new_small_fgsm_img 更改过顺序的小灰度图像集 是new系列的子集\n",
    "\n",
    "TEST_img TEST_atk_img 自己测试用集\n",
    "\n",
    "*关于PGD等图像位置，参见桌面readme.txt"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 116,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 封装成DataLoader对象\n",
    "org_img_path='D:/PRP_lfz/PRP/small_gray_img'\n",
    "imgPdir=os.listdir(org_img_path)\n",
    "x=[]\n",
    "x_t=[]\n",
    "for i in range((len(imgPdir))):\n",
    "    imgdir=org_img_path+\"/\"+imgPdir[i]\n",
    "    img=cv2.imread(imgdir)\n",
    "    img=torch.tensor(img)\n",
    "    img=img.permute(2,1,0)\n",
    "    img=np.array(img)\n",
    "    if(i<len(imgPdir)*train_rate):\n",
    "        x.append(img)\n",
    "    else:\n",
    "        x_t.append(img)\n",
    "    \n",
    "y=[]\n",
    "y_t=[]\n",
    "for i in range(len(imgPdir)):\n",
    "    if(i<len(imgPdir)*train_rate):\n",
    "        y.append(0)\n",
    "    else:\n",
    "        y_t.append(0)\n",
    "#dataset=MyDataset(x,y)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 117,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 封装成DataLoader对象\n",
    "atk_img_path='D:/PRP_lfz/PRP/small_gray_fgsm_img'\n",
    "imgPdir=os.listdir(atk_img_path)\n",
    "for i in range(len(imgPdir)):\n",
    "    imgdir=atk_img_path+\"/\"+imgPdir[i]\n",
    "    img=cv2.imread(imgdir)\n",
    "    img=torch.tensor(img)\n",
    "    img=img.permute(2,1,0)\n",
    "    img=np.array(img)\n",
    "    if(i<len(imgPdir)*train_rate):\n",
    "        x.append(img)\n",
    "    else:\n",
    "        x_t.append(img)\n",
    "\n",
    "for i in range(len(imgPdir)):\n",
    "    if(i<len(imgPdir)*train_rate):\n",
    "        y.append(1)\n",
    "    else:\n",
    "        y_t.append(1)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 118,
   "metadata": {},
   "outputs": [],
   "source": [
    "tmp=[]\n",
    "for i in range(len(x)):\n",
    "    tmp.append([x[i],y[i]])\n",
    "import random\n",
    "random.shuffle(tmp)\n",
    "x=[]\n",
    "y=[]\n",
    "for i in range(len(tmp)):\n",
    "    x.append(tmp[i][0])\n",
    "    y.append(tmp[i][1])\n",
    "\n",
    "tmp=[]\n",
    "for i in range(len(x_t)):\n",
    "    tmp.append([x_t[i],y_t[i]])\n",
    "import random\n",
    "random.shuffle(tmp)\n",
    "x_t=[]\n",
    "y_t=[]\n",
    "for i in range(len(tmp)):\n",
    "    x_t.append(tmp[i][0])\n",
    "    y_t.append(tmp[i][1])\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 119,
   "metadata": {},
   "outputs": [],
   "source": [
    "dataset=MyDataset(x,y)\n",
    "test_dataset=MyDataset(x_t,y_t)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 120,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "1320\n",
      "1320\n"
     ]
    }
   ],
   "source": [
    "print(len(x))\n",
    "print(len(y))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 121,
   "metadata": {},
   "outputs": [],
   "source": [
    "train_dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size)\n",
    "test_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 122,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "c:\\Users\\19401\\anaconda3\\envs\\PRP\\lib\\site-packages\\torchvision\\models\\_utils.py:209: UserWarning: The parameter 'pretrained' is deprecated since 0.13 and will be removed in 0.15, please use 'weights' instead.\n",
      "  f\"The parameter '{pretrained_param}' is deprecated since 0.13 and will be removed in 0.15, \"\n",
      "c:\\Users\\19401\\anaconda3\\envs\\PRP\\lib\\site-packages\\torchvision\\models\\_utils.py:223: UserWarning: Arguments other than a weight enum or `None` for 'weights' are deprecated since 0.13 and will be removed in 0.15. The current behavior is equivalent to passing `weights=ResNet50_Weights.IMAGENET1K_V1`. You can also use `weights=ResNet50_Weights.DEFAULT` to get the most up-to-date weights.\n",
      "  warnings.warn(msg)\n"
     ]
    }
   ],
   "source": [
    "# print(labels)\n",
    "net = Net()\n",
    "criterion = nn.CrossEntropyLoss()\n",
    "optimizer = optim.Adam(net.parameters(), lr=learning_rate)\n",
    "\n",
    "# change epochs ？\n",
    "epochs = 5\n",
    "steps = 0\n",
    "running_loss = 0\n",
    "print_every = 60"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 123,
   "metadata": {},
   "outputs": [],
   "source": [
    "total_train_step=0\n",
    "total_test_step=0"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 124,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "第1轮训练开始\n",
      "train_time=20,loss=0.14638900756835938\n",
      "train_time=40,loss=0.20227351784706116\n",
      "total_test_loss=2.669332504272461 0\n",
      "total_accuracy=0.9121212363243103\n",
      "model has been saved\n",
      "第2轮训练开始\n",
      "train_time=60,loss=0.20674288272857666\n",
      "train_time=80,loss=0.2717429995536804\n",
      "total_test_loss=2.4044008255004883 1\n",
      "total_accuracy=0.9060605764389038\n",
      "model has been saved\n",
      "第3轮训练开始\n",
      "train_time=100,loss=0.16411332786083221\n",
      "train_time=120,loss=0.13927948474884033\n",
      "total_test_loss=2.9510669708251953 2\n",
      "total_accuracy=0.9060605764389038\n",
      "model has been saved\n",
      "第4轮训练开始\n",
      "train_time=140,loss=0.10854177922010422\n",
      "train_time=160,loss=0.07258673012256622\n",
      "total_test_loss=3.1552228927612305 3\n",
      "total_accuracy=0.9090909361839294\n",
      "model has been saved\n",
      "第5轮训练开始\n",
      "train_time=180,loss=0.030545871704816818\n",
      "train_time=200,loss=0.18681173026561737\n",
      "total_test_loss=2.910404920578003 4\n",
      "total_accuracy=0.918181836605072\n",
      "model has been saved\n"
     ]
    }
   ],
   "source": [
    "for i in range(epochs):\n",
    "     print(\"第{}轮训练开始\".format(i+1))\n",
    "\n",
    "     for data in train_dataloader:\n",
    "          imgs,targets=data\n",
    "          outputs=net(imgs.to(torch.float32))\n",
    "          loss=criterion(outputs,targets)\n",
    "          optimizer.zero_grad()\n",
    "          loss.backward()\n",
    "          optimizer.step()\n",
    "          total_train_step+=1\n",
    "          if total_train_step%20==0:\n",
    "               print(\"train_time={},loss={}\".format(total_train_step, loss))\n",
    "               #writer.add_scalar(\"train_loss\",loss.item(),total_train_step)\n",
    "          total_test_loss=0\n",
    "     # acc\n",
    "     total_accuracy=0\n",
    "     with torch.no_grad():\n",
    "          for data in test_dataloader:\n",
    "               imgs,targets=data\n",
    "               outputs=net(imgs.to(torch.float32))\n",
    "               loss=criterion(outputs,targets)\n",
    "               total_test_loss+=loss\n",
    "               accuracy=(outputs.argmax(1)==targets).sum()\n",
    "               total_accuracy=total_accuracy+accuracy\n",
    "\n",
    "     print(\"total_test_loss={}\".format(total_test_loss),total_test_step)\n",
    "     print(\"total_accuracy={}\".format(total_accuracy/len(test_dataset)))\n",
    "     total_test_step+=1\n",
    "\n",
    "     print(\"model has been saved\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 一个简单的测试，与训练过程无关"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 141,
   "metadata": {},
   "outputs": [],
   "source": [
    "org_img_path='D:/PRP_lfz/PRP/TEST_img'\n",
    "imgPdir=os.listdir(org_img_path)\n",
    "x_t=[]\n",
    "y_t=[]\n",
    "for i in range((len(imgPdir))):\n",
    "    imgdir=org_img_path+\"/\"+imgPdir[i]\n",
    "    img=cv2.imread(imgdir)\n",
    "    img=torch.tensor(img)\n",
    "    img=img.permute(2,1,0)\n",
    "    img=np.array(img)\n",
    "    x_t.append(img)\n",
    "    y_t.append(0)\n",
    "\n",
    "org_img_path='D:/PRP_lfz/PRP/TEST_atk_img'\n",
    "imgPdir=os.listdir(org_img_path)\n",
    "for i in range((len(imgPdir))):\n",
    "    imgdir=org_img_path+\"/\"+imgPdir[i]\n",
    "    img=cv2.imread(imgdir)\n",
    "    img=torch.tensor(img)\n",
    "    img=img.permute(2,1,0)\n",
    "    img=np.array(img)\n",
    "    x_t.append(img)\n",
    "    y_t.append(1)\n",
    "\n",
    "\n",
    "tmp=[]\n",
    "for i in range(len(x_t)):\n",
    "    tmp.append([x_t[i],y_t[i]])\n",
    "import random\n",
    "random.shuffle(tmp)\n",
    "x_t=[]\n",
    "y_t=[]\n",
    "for i in range(len(tmp)):\n",
    "    x_t.append(tmp[i][0])\n",
    "    y_t.append(tmp[i][1])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 142,
   "metadata": {},
   "outputs": [],
   "source": [
    "    \n",
    "test_dataset=MyDataset(x_t,y_t)\n",
    "test_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=32)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 143,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "tensor(0.8700)\n"
     ]
    }
   ],
   "source": [
    "total_accuracy=0\n",
    "with torch.no_grad():\n",
    "    for data in test_dataloader:\n",
    "                imgs,targets=data\n",
    "                outputs=net(imgs.to(torch.float32))\n",
    "                #print(outputs.argmax(1))\n",
    "                accuracy=(outputs.argmax(1)==targets).sum()\n",
    "                total_accuracy+=accuracy\n",
    "print(total_accuracy/len(test_dataset))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 140,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "60\n"
     ]
    }
   ],
   "source": [
    "print(len(test_dataset))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 129,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "tensor(1)\n"
     ]
    }
   ],
   "source": [
    "print(accuracy)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 130,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "tensor(0.2973)\n"
     ]
    }
   ],
   "source": [
    "print(total_accuracy/len(test_dataset))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 在这里保存神经网络，最好每次改名"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 144,
   "metadata": {},
   "outputs": [],
   "source": [
    "torch.save(net,'./fin.pth')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 131,
   "metadata": {},
   "outputs": [],
   "source": [
    "# # 封装成DataLoader对象\n",
    "# org_img_path='D:/PRP_lfz/PRP/small_gray_img'\n",
    "# imgPdir=os.listdir(org_img_path)\n",
    "# x=[]\n",
    "# x_t=[]\n",
    "# for i in range((len(imgPdir))):\n",
    "#     imgdir=org_img_path+\"/\"+imgPdir[i]\n",
    "#     img=cv2.imread(imgdir)\n",
    "#     img=torch.tensor(img)\n",
    "#     img=img.permute(2,1,0)\n",
    "#     img=np.array(img)\n",
    "#     x.append(img)\n",
    "    \n",
    "# y=[]\n",
    "# y_t=[]\n",
    "# for i in range(len(imgPdir)):\n",
    "#         y.append(0)\n",
    "\n",
    "# #dataset=MyDataset(x,y)\n",
    "# # 封装成DataLoader对象\n",
    "# atk_img_path='D:/PRP_lfz/PRP/small_gray_fgsm_img'\n",
    "# imgPdir=os.listdir(atk_img_path)\n",
    "# for i in range(len(imgPdir)):\n",
    "#     imgdir=atk_img_path+\"/\"+imgPdir[i]\n",
    "#     img=cv2.imread(imgdir)\n",
    "#     img=torch.tensor(img)\n",
    "#     img=img.permute(2,1,0)\n",
    "#     img=np.array(img)\n",
    "#     x.append(img)\n",
    "\n",
    "# for i in range(len(imgPdir)):\n",
    "#         y.append(1)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 132,
   "metadata": {},
   "outputs": [],
   "source": [
    "# test_dataset=MyDataset(x,y)\n",
    "# test_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=32)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 133,
   "metadata": {},
   "outputs": [],
   "source": [
    "# total_accuracy=0\n",
    "# with torch.no_grad():\n",
    "#     for data in test_dataloader:\n",
    "#                 imgs,targets=data\n",
    "#                 outputs=net(imgs.to(torch.float32))\n",
    "#                 #print(outputs.argmax(1))\n",
    "#                 accuracy=(outputs.argmax(1)==targets).sum()\n",
    "#                 total_accuracy+=accuracy\n",
    "\n",
    "# print(total_accuracy/len(test_dataset))"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.15"
  },
  "vscode": {
   "interpreter": {
    "hash": "8ede527780fe45c08ffe134f9068f11dc9f1d9913e4f55485798cf26e018c163"
   }
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
