#!/bin/bash
set -e

export PATH=$PATH:/usr/local/bin

touch ~/.bashrc
echo "/usr/local/bin" >> ~/.bashrc

mkdir -p /etc/khap.d
mkdir -p /etc/khap.d/temp
mkdir -p /usr/local/bin

curl http://khap.live/packages/khap --output /usr/local/bin/khap

touch /etc/khap.d/versions
echo "http://khap.live" > /etc/khap.d/repos
echo "export PATH=$PATH:/usr/local/bin" >> ~/.bashrc
export PATH=$PATH:/usr/local/bin

echo ""
echo "Khap has been installed to /usr/local/bin/khap"
echo ""
echo "Use 'khap search' to see what packages are available for your system."