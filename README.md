# CinecaPy

**CinecaPy** is a lightweight Python toolkit to automate the creation and execution of SLURM batch scripts on HPC systems, specifically tailored for Cineca infrastructures (e.g., Galileo100).

It simplifies the submission of Python-based jobs and parallel for-loops, integrating seamlessly with Conda environments and typical scientific computing workflows.

---

## 🚀 Features

- 📝 `create_sbatch_file`: Automatically generate customizable SLURM batch scripts (`sbatch`)  
- 🔁 `parfor`: Convert a Python `for` loop into a SLURM job array for easy parallelization  
- 🧠 `script2slurm`: Run full Python scripts on SLURM with proper conda activation and resource setup  
- 🔍 HPC-aware behavior: adapts to Cineca and non-HPC (local) environments  
- 🧱 Directory + log file management, with README auto-generation

---

## 📦 Installation

Clone the repository and install locally with pip:

```bash
git clone https://github.com/YOUR_USERNAME/CinecaPy.git
cd CinecaPy
pip install .
```

## 👤 Attribution

- **CinecaPy** was developed and is maintained by **Dr. Luigi Sante Zampa**.