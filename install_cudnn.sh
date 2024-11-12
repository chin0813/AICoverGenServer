#!/bin/bash

# Define the cuDNN version and CUDA version
CUDNN_VERSION="8.2.4.15"
CUDA_VERSION="11.4"

# Download and extract cuDNN in parallel
wget https://developer.download.nvidia.com/compute/redist/cudnn/v8.2.4/cudnn-${CUDA_VERSION}-linux-x64-v${CUDNN_VERSION}.tgz &
tar -xzvf cudnn-${CUDA_VERSION}-linux-x64-v${CUDNN_VERSION}.tgz &

# Wait for both background processes to finish
wait

# Copy the cuDNN files to the CUDA directory
sudo cp cuda/include/cudnn*.h /usr/local/cuda/include && \
sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64 && \
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*

# Verify the cuDNN installation
grep -m 1 CUDNN_MAJOR /usr/local/cuda/include/cudnn_version.h -A 2

# Clean up
rm -rf cuda cudnn-${CUDA_VERSION}-linux-x64-v${CUDNN_VERSION}.tgz