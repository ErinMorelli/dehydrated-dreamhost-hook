#!/bin/sh
apt-get install python-pip
git clone https://github.com/lukas2511/dehydrated.git /root/dehydrated
mkdir /root/dehydrated/hooks
git clone https://github.com/rewardone/dehydrated-dreamhost-hook.git /root/dehydrated/hooks/dreamhost
pip install -r /root/dehydrated/hooks/dreamhost/requirements.txt
mkdir -p /root/.config/dehydrated
cp /root/dehydrated/hooks/dreamhost/sample_deploy.conf /root/.config/dehydrated/deploy.conf
echo "Please export your DREAMHOST_API_KEY with: export DREAMHOST_API_KEY='Key'"
echo "Please update your /root/.config/dehydrated/deploy.conf file"


