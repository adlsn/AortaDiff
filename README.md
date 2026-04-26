# AortaDiff: Volume-Guided Conditional Diffusion Models for Multi-Branch Aortic Surface Generation

> Official implementation of **AortaDiff (IEEE TVCG 2026)**  
> **Authors:** Delin An, Pan Du, Jian-Xun Wang, Chaoli Wang  

---

## 📌 Overview

AortaDiff is a **fully automatic framework** for constructing high-quality 3D aortic surfaces directly from CT/MRI volumes using **volume-guided conditional diffusion models**.

Unlike traditional pipelines that rely heavily on segmentation and manual processing, AortaDiff provides:

- End-to-end pipeline from **medical volume → CFD-ready mesh**
- Robust performance with **limited training data**
- High-quality **multi-branch aortic geometry reconstruction**
- Direct compatibility with **computational fluid dynamics (CFD)**

As described in the [paper](https://ieeexplore.ieee.org/document/11269366), the framework decomposes the problem into structured stages to improve robustness and geometric fidelity.

---

## 🧠 Framework

<!-- TODO: Insert framework figure here -->
<p align="center">
  <img src="assets/framework.png" width="80%">
</p>

The AortaDiff pipeline consists of three major stages:

### 1. Centerline Generation (Diffusion Model)
- A **volume-guided conditional diffusion model (CDM)** generates aortic centerlines
- CT/MRI volumes are encoded using a **ViT-based feature extractor**
- Centerline is represented as a **1D sequence (16 × 3)**

### 2. Contour Extraction
- Orthogonal slices are extracted along centerline points
- A [**SAM-based ScribblePrompt model**](https://scribbleprompt.csail.mit.edu/) segments vessel lumen
- Contours are extracted and standardized (32 points per slice)

### 3. Surface Reconstruction
- Contours are aligned and fitted using **NURBS**
- Produces smooth, watertight, **CFD-compatible meshes**

### 4. Downstream CFD Simulation (Optional)
- Generated meshes can be directly used in CFD solvers (e.g., OpenFOAM)
- Enables analysis of:
  - Velocity
  - Pressure
  - Wall Shear Stress (WSS)

---

## 📊 Results

<!-- TODO: Insert qualitative results -->
<p align="center">
  <img src="assets/results.png" width="80%">
</p>

AortaDiff demonstrates:

- Accurate reconstruction of **multi-branch aorta**
- Robust performance on **limited datasets**
- Strong generalization to unseen CT volumes
- High-quality meshes suitable for **hemodynamic simulation**

Additional experiments and diffusion visualization are provided in the appendix :contentReference[oaicite:1]{index=1}.

---

## 🗂 Repository Structure
```text
AortaDiff/
│
├── experiments/                      # Core experiment scripts
│   ├── DiffusionCentrelineTrain.py  # Train centerline diffusion model
│   ├── DiffusionCenterlineSample.py # Inference/sampling script
│   └── Sp_contour.py                # Contour extraction & preprocessing
│
├── denoising_diffusion_pytorch/     # Diffusion backbone (1D diffusion, UNet, trainer)
│
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
└── LICENSE

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/AortaDiff.git
cd AortaDiff

### 2. Create Environment

conda create -n aortadiff python=3.9 -y
conda activate aortadiff

### 3. Install PyTorch

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118



template.pdf
PDF

appendix.pdf
PDF

DiffusionCenterlineSample.py
Python

DiffusionCentrelineTrain.py
Python

Sp_contour.py
Python
我要给aortadiff这篇论文做一个公开的github仓库，论文是两个pdf文件，代码部分如experiments里所示，其他还有一个denoising_diffusion_pytorch文件夹，里面放的是常用的diffusion库文件。我需要的github仓库要包含论文内容的介绍，论文内framework图片（用占位符，我自己添加），实验结果展示图片（占位符），以及代码的环境，安装配置介绍等。最后可以给出aortadiff的引用信息，让别人来引用，如下：
@ARTICLE{11269366,
  author={An, Delin and Du, Pan and Wang, Jian-Xun and Wang, Chaoli},
  journal={IEEE Transactions on Visualization and Computer Graphics}, 
  title={AortaDiff: Volume-Guided Conditional Diffusion Models for Multi-Branch Aortic Surface Generation}, 
  year={2026},
  volume={32},
  number={1},
  pages={922-932},

  doi={10.1109/TVCG.2025.3634652}}
 尽可能做的符合高水平论文的开源代码仓库风格，结果直接给我markdown格式即可。

# AortaDiff: Volume-Guided Conditional Diffusion Models for Multi-Branch Aortic Surface Generation

> Official implementation of **AortaDiff (IEEE TVCG 2026)**  
> **Authors:** Delin An, Pan Du, Jian-Xun Wang, Chaoli Wang  

---

## 📌 Overview

AortaDiff is a **fully automatic framework** for constructing high-quality 3D aortic surfaces directly from CT/MRI volumes using **volume-guided conditional diffusion models**.

Unlike traditional pipelines that rely heavily on segmentation and manual processing, AortaDiff provides:

- End-to-end pipeline from **medical volume → CFD-ready mesh**
- Robust performance with **limited training data**
- High-quality **multi-branch aortic geometry reconstruction**
- Direct compatibility with **computational fluid dynamics (CFD)**

As described in the paper :contentReference[oaicite:0]{index=0}, the framework decomposes the problem into structured stages to improve robustness and geometric fidelity.

---

## 🧠 Framework

<!-- TODO: Insert framework figure here -->
<p align="center">
  <img src="assets/framework.png" width="80%">
</p>

The AortaDiff pipeline consists of three major stages:

### 1. Centerline Generation (Diffusion Model)
- A **volume-guided conditional diffusion model (CDM)** generates aortic centerlines
- CT/MRI volumes are encoded using a **ViT-based feature extractor**
- Centerline is represented as a **1D sequence (16 × 3)**

### 2. Contour Extraction
- Orthogonal slices are extracted along centerline points
- A **SAM-based ScribblePrompt model** segments vessel lumen
- Contours are extracted and standardized (32 points per slice)

### 3. Surface Reconstruction
- Contours are aligned and fitted using **NURBS**
- Produces smooth, watertight, **CFD-compatible meshes**

### 4. Downstream CFD Simulation (Optional)
- Generated meshes can be directly used in CFD solvers (e.g., OpenFOAM)
- Enables analysis of:
  - Velocity
  - Pressure
  - Wall Shear Stress (WSS)

---

## 📊 Results

<p align="center">
  <img src="assets/results.png" width="80%">
</p>

AortaDiff demonstrates:

- Accurate reconstruction of **multi-branch aorta**
- Robust performance on **limited datasets**
- Strong generalization to unseen CT volumes
- High-quality meshes suitable for **hemodynamic simulation**

Additional experiments and diffusion visualization are provided in the appendix:contentReference[oaicite:1]{index=1}.

---

## 🗂 Repository Structure
AortaDiff/
│
├── experiments/
│ ├── DiffusionCentrelineTrain.py
│ ├── DiffusionCenterlineSample.py
│ └── Sp_contour.py
│
├── denoising_diffusion_pytorch/
│ └── (diffusion backbone implementation)
│
├── data/
│ ├── training_data/
│ └── testing_data/
│
├── assets/
│ ├── framework.png # (placeholder)
│ └── results.png # (placeholder)
│
├── paper/
│ ├── main.pdf # paper
│ └── appendix.pdf # appendix
│
└── README.md


---

## ⚙️ Installation

### Requirements

- Python ≥ 3.8
- PyTorch ≥ 1.12
- CUDA (recommended)

### Dependencies

```bash
pip install torch torchvision
pip install numpy scipy matplotlib
pip install monai
pip install pyvista
pip install opencv-python
pip install scribbleprompt
🚀 Usage
1. Train Centerline Diffusion Model
python experiments/DiffusionCentrelineTrain.py
Uses a 1D U-Net + Gaussian Diffusion

Trained on centerline + CT volume pairs 


2. Generate Centerlines
python experiments/DiffusionCenterlineSample.py
Generates centerline predictions conditioned on CT volumes 


3. Extract Contours & Build Mesh
python experiments/Sp_contour.py
Extracts orthogonal slices

Performs segmentation via ScribblePrompt

Generates contours and prepares for NURBS fitting 


📦 Data Format
Centerline
Shape: (N, 16, 3)

Normalized to [0, 1]

CT Volume
Shape: (N, 1, 128, 128, 128)

Preprocessed and intensity normalized

🧩 Key Design Choices
Centerline representation instead of point clouds
→ reduces data requirement and improves stability

Volume-guided diffusion
→ ensures anatomical consistency

Contour-based reconstruction (NURBS)
→ produces smooth, CFD-ready meshes

🔬 Applications
Hemodynamic analysis

Surgical planning

Medical visualization

Synthetic data generation

CFD simulation pipelines

📚 Citation
If you find this work useful, please cite:

@ARTICLE{11269366,
  author={An, Delin and Du, Pan and Wang, Jian-Xun and Wang, Chaoli},
  journal={IEEE Transactions on Visualization and Computer Graphics}, 
  title={AortaDiff: Volume-Guided Conditional Diffusion Models for Multi-Branch Aortic Surface Generation}, 
  year={2026},
  volume={32},
  number={1},
  pages={922-932},
  doi={10.1109/TVCG.2025.3634652}
}
🙏 Acknowledgements
Built upon diffusion models and medical imaging frameworks (MONAI, PyTorch)

📬 Contact
Delin An
University of Notre Dame
📧 dan3@nd.edu

⭐ If you find this repository helpful, please consider giving it a star!

