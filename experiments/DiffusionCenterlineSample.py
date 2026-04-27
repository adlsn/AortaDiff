import torch
import numpy as np
import sys

sys.path.append("..")
sys.path.insert(1, "./")
from denoising_diffusion_pytorch import (
    Unet1D,
    GaussianDiffusion1D,
    Trainer1D,
    Dataset1D,
)
import pathlib

# Load centerline data already in CT index space [0, 128]
data = np.load("/home/mingqi/ai_agent/ref/AortaDiff/data/training_data/nrrd_128/cl_id.npy")  # shape: (21, 16, 3)

data = torch.tensor(data, dtype=torch.float32)
data_norm = data / 128.0  # normalize to [0, 1]
data_norm = data_norm.transpose(1, 2)  # shape: (21, 3, 16)
list = []
for ii in range(0, 100):
    list.append(data_norm)
data_norm = torch.stack(list).view(2100, 3, 16)

ct_vol = torch.from_numpy(
    np.load("/home/mingqi/ai_agent/ref/AortaDiff/data/training_data/nrrd_128/image_128.npy")
).unsqueeze(1)  # shape: (21, 1, 128, 128, 128)
ct_v_list = []
for ii in range(0, 100):
    ct_v_list.append(ct_vol)
ct_vol = torch.stack(ct_v_list).view(2100, 1, 128, 128, 128)

model = Unet1D(dim=64, dim_mults=(1, 2, 4, 8), out_dim=3, channels=19)  # default: 3

diffusion = GaussianDiffusion1D(
    model, seq_length=data_norm.shape[-1], timesteps=1000, objective="pred_v"
)

dataset = Dataset1D(data_norm, ct_vol)

trainer = Trainer1D(
    diffusion,
    dataset=dataset,
    train_batch_size=1,
    train_lr=8e-5,
    train_num_steps=700000,
    gradient_accumulate_every=2,
    ema_decay=0.995,
    amp=True,
    results_folder='/home/mingqi/ai_agent/ref/AortaDiff/results',
    save_and_sample_every=500,
)

name = "1"
results = []
for ii in range(56,111):
    print(ii)
    trainer.load(ii)
    trainer.num_samples = 1

    ct_volume = ct_vol[0].unsqueeze(0)

    print(ct_volume.shape)

    # Sample with CT conditioning
    samples = trainer.test(
        ct_img=ct_volume,
        return_all_timesteps=False
    )

    # samples are in [0, 1] space, multiply by 128 to get CT index coordinates
    samples_ct = samples * 128.0
    results.append(samples_ct.detach().cpu().numpy())
    print(samples.shape)

    results_all = np.stack(results, axis=0)
    print(results_all.shape)
    np.save(f"/home/mingqi/ai_agent/ref/AortaDiff/data/testing_data/test_result_cl/{name}.npy", results_all)

# CUDA_VISIBLE_DEVICES=0 python /home/mingqi/ai_agent/ref/AortaDiff/experiments/DiffusionCenterlineSample.py
