FROM ubuntu:18.04
 
# apt update 以及 repo list 更新為國網
RUN sed -i 's/archive.ubuntu.com/free.nchc.org.tw/g' /etc/apt/sources.list

# 安裝必要的 python 3 相關套件
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y python3-pip build-essential libssl-dev libffi-dev python3-dev python3-venv && apt-get autoremove -y \
    && echo "export PYTHONIOENCODING=UTF-8" >> ~/.bashrc \
    && echo "export LC_ALL=C.UTF-8" >> ~/.bashrc \
    && echo "export LANG=C.UTF-8" >> ~/.bashrc

# 建立工作目錄
RUN mkdir -p /var/www/html
WORKDIR /var/www/html

# 預先安裝好 pip requirements
COPY requirements.txt /var/www/html/requirements.txt
RUN python3 -m pip install --upgrade pip && pip install -r requirements.txt

# 安裝 CPU only 的 Tensorflow 與 Keras
RUN pip install --upgrade tensorflow https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow_cpu-2.1.0-cp36-cp36m-manylinux2010_x86_64.whl && pip install keras

# 安裝其餘套件

