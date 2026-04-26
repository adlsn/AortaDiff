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
