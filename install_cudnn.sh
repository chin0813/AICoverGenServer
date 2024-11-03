#!/bin/bash

# Define the cuDNN version and CUDA version
CUDNN_VERSION="8.2.4.15"
CUDA_VERSION="11.4"

# Download cuDNN
wget https://developer.download.nvidia.com/compute/redist/cudnn/v8.2.4/cudnn-${CUDA_VERSION}-linux-x64-v${CUDNN_VERSION}.tgz

# Extract the cuDNN files
tar -xzvf cudnn-${CUDA_VERSION}-linux-x64-v${CUDNN_VERSION}.tgz

# Copy the cuDNN files to the CUDA directory
sudo cp cuda/include/cudnn*.h /usr/local/cuda/include
sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*

# Verify the cuDNN installation
cat /usr/local/cuda/include/cudnn_version.h | grep CUDNN_MAJOR -A 2

# Clean up
rm -rf cuda cudnn-${CUDA_VERSION}-linux-x64-v${CUDNN_VERSION}.tgz