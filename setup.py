from distutils.core import setup
setup(
  name = 'python-NDL',
  packages = ['pyNDL'],
  version = '0.4',
  license='MIT',
  description = 'A nodal interface for python',
  author = 'Louis Gambardella',
  author_email = 'louis.gambardella03@gmail.com',
  url = 'https://github.com/merwynnn/pyNDL',
  download_url = 'https://github.com/merwynnn/pyNDL/archive/refs/tags/v_04.tar.gz',
  keywords = ['Nodal', 'Language', 'pyNDL', 'Blueprint'],
  install_requires=[
          'numpy',
          'pygame',
          'Pillow',
          'pyperclip'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
  ],
  package_dir={'pyNDL': 'pyNDL'},
  package_data={'pyNDL': ['Prefabs/*.py', 'Assets/Images/*.png', 'Assets/Images/*.jpg']},

)