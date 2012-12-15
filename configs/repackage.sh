#!/bin/bash

set -x -e

vagrant package --vagrantfile Vagrantfile
mv package.box gitorama.box
vagrant box add --force gitorama gitorama.box
