# -*- coding: utf-8 -*-
#!/usr/bin/python
#
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This is the setup file for the project.

The standard setup rules apply:
python setup.py build
sudo python setup.py install
"""

from setuptools import find_packages
from setuptools import setup
from pip.req import parse_requirements
from pip.download import PipSession

setup(
    name='Turbinia',
    version='20170801+fb20180525',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=['turbiniactl'],
    install_requires=[str(req.req) for req in parse_requirements(
        'requirements.txt', session=PipSession())
    ])
