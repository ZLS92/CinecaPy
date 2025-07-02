from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 2 - Pre-Alpha',
  'Intended Audience :: Science/Research',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='CinecaPy',
  version='0.0.1',
  description='Python tools for managing SLURM jobs on Cineca HPC systems',
  long_description=open('README.md').read(),
  long_description_content_type="text/markdown",
  url='https://github.com/tuonomeutente/CinecaPy',
  author='Luigi Sante Zampa',
  author_email='zampaluigis@gmail.com',
  license='MIT',
  classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3',
      'Operating System :: OS Independent',
  ],
  keywords='SLURM, HPC, Cineca, job scheduling, sbatch, parallel computing',
  packages=find_packages(),
  python_requires='>=3.6',
)
