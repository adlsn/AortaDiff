import numpy as np
import torch
from scipy.ndimage import map_coordinates
import pathlib
import pyvista as pv
import logging
import matplotlib.pyplot as plt
import os
from scribbleprompt import ScribblePromptSAM
import cv2
from monai.transforms import ScaleIntensityRange

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.disable()


def load_data(ct_folder, centerline_file, t_matrix_file):
    """
    Load the centerline and CT volume data.
    """
    centerline = np.load(centerline_file)
    translation_matrix = np.load(t_matrix_file)
    translation_matrix = np.expand_dims(translation_matrix, axis=1)
    centerline = centerline - translation_matrix
    ct_list = []
    origin_list = []
    spacing_list = []
    ct_num = len(list(pathlib.Path(ct_folder).iterdir()))

    scale_intensity = ScaleIntensityRange(a_min=-100,
                                          a_max=600,
                                          b_min=0.0,
                                          b_max=1.0,
                                          clip=True)

    for i in range(ct_num):
        ct_volume = pv.read(
            str(pathlib.Path(ct_folder).joinpath(
                f"{i + 1}.vti"))).point_data['ImageScalars'].reshape(
                    (512, 512, 512)).transpose(2, 1, 0)
        ct_origin = pv.read(
            str(pathlib.Path(ct_folder).joinpath(f"{i + 1}.vti"))).origin
        ct_spacing = pv.read(
            str(pathlib.Path(ct_folder).joinpath(f"{i + 1}.vti"))).spacing

        # preprocess the CT volume
        ct_volume = np.expand_dims(ct_volume, axis=0)
        ct_volume = scale_intensity(torch.from_numpy(ct_volume))
        ct_volume = ct_volume.squeeze(0).numpy()

        ct_list.append(ct_volume)
        origin_list.append(ct_origin)
        spacing_list.append(ct_spacing)
        logging.debug(f"Loaded CT volume from {i + 1}.vti.")
        # break # TODO: quick test
        # if i > 5:
        #     break
    ct_list = np.array(ct_list)
    origin_list = np.array(origin_list)
    spacing_list = np.array(spacing_list)
    logging.debug(f"Loaded {len(ct_list)} CT volumes.")
    return centerline, ct_list, origin_list, spacing_list


def downsample_contour(contour, num_points=32):
    step = len(contour) / num_points
    indices = [int(i * step) for i in range(num_points)]
    downsampled_contour = contour[indices]
    return downsampled_contour


def sort_contours(contour, center):
    """
    Make the contour in a sorted order (counterclockwise, starting from the first row).
    """
    angles = np.arctan2(contour[:, 1] - center[1], contour[:, 0] - center[0])
    sorted_indices = np.argsort(angles)
    sorted_contour = contour[sorted_indices]

    # ============================visualize the result============================
    # plt.scatter(contour[:, 0], contour[:, 1], color='blue', label='Original Points', s=50)
    # plt.scatter(center[0], center[1], color='red', label='Center', s=100)
    #
    # plt.plot(np.append(sorted_contour[:, 0], sorted_contour[0, 0]),
    #          np.append(sorted_contour[:, 1], sorted_contour[0, 1]),
    #          color='green', linestyle='-', label='Sorted Path')
    #
    # for i, (x, y) in enumerate(sorted_contour):
    #     plt.text(x, y, f'{i + 1}', fontsize=12, color='black', ha='right', va='bottom')
    #
    # plt.axhline(0, color='gray', linestyle='--', linewidth=0.5)
    # plt.axvline(0, color='gray', linestyle='--', linewidth=0.5)
    # plt.title('Sorted Points in Counterclockwise Order')
    # plt.legend()
    # plt.gca().set_aspect('equal', adjustable='box')
    # plt.grid(True)
    # plt.show()

    return sorted_contour


def smooth(contours,
           centerline,
           scale_factor_low=0.5,
           scale_factor_high=1.4,
           irregularity_factor=0.1):
    """

    :param contours: numpy array, shape (16, 32, 3)
    :param centerline: numpy array, shape (16, 3)
    :param scale_factor_low: float, contours below this ratio are replaced
    :param scale_factor_high: float, contours above this ratio are replaced
    :param irregularity_factor: float, irregularity strength in [0, 1]
    :return: numpy array, shape (16, 32, 3)
    """
    num_contours, num_points, _ = contours.shape

    radii = np.linalg.norm(contours - centerline[:, np.newaxis, :], axis=2)
    min_radii = np.min(radii, axis=1)

    sorted_min_radii = np.sort(min_radii)[::-1]
    one_third_index = len(sorted_min_radii) // 3
    base_radius = sorted_min_radii[one_third_index]

    too_small_contour_indices = np.where(min_radii < scale_factor_low *
                                         base_radius)[0]
    too_large_contour_indices = np.where(min_radii > scale_factor_high *
                                         base_radius)[0]
    replace_contour_indices = np.concatenate(
        [too_small_contour_indices, too_large_contour_indices])

    valid_contour_indices = np.where(
        (min_radii >= scale_factor_low * base_radius)
        & (min_radii <= scale_factor_high * base_radius))[0]
    replacement_radius = np.median(min_radii[valid_contour_indices])

    new_contours = contours.copy()
    for idx in replace_contour_indices:
        if idx == 0:
            neighbor_vector = centerline[idx + 1] - centerline[idx]
        elif idx == num_contours - 1:
            neighbor_vector = centerline[idx] - centerline[idx - 1]
        else:
            neighbor_vector = (centerline[idx + 1] - centerline[idx - 1]) / 2
        neighbor_vector /= np.linalg.norm(neighbor_vector)

        direction1 = np.random.rand(3)
        direction1 -= direction1.dot(neighbor_vector) * neighbor_vector
        direction1 /= np.linalg.norm(direction1)

        direction2 = np.cross(neighbor_vector, direction1)
        direction2 /= np.linalg.norm(direction2)

        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        new_contour = []
        for angle in angles:
            perturbation = np.random.uniform(
                -irregularity_factor, irregularity_factor) * replacement_radius
            radius = replacement_radius + perturbation
            point = (centerline[idx] + radius * np.cos(angle) * direction1 +
                     radius * np.sin(angle) * direction2)
            new_contour.append(point)
        new_contours[idx] = np.array(new_contour)

    return new_contours


def main():
    ct_folder = r"E:\MyStore\ND_lab\A-diffusion\data\ct_shape_data\resample_512\ct_volume"  # 512x512x512
    centerline_file = r"E:\MyStore\ND_lab\A-diffusion\CT_shape_diffusion\interpolated_new_aortas-selected\trainingdata (1)\trainingdata\originalcl.npy"  # 22x16x3
    translation_matrix = r"E:\MyStore\ND_lab\A-diffusion\CT_shape_diffusion\interpolated_new_aortas-selected\training_data\translation(22x3).npy"
    centerlines, ct_list, origin_list, spacing_list = load_data(
        ct_folder, centerline_file, translation_matrix)
    output_folder = r"E:\MyStore\ND_lab\A-diffusion\data\ct_shape_data\resample_512\cl_slices"
    # final_contour_output_folder = r"D:\MyStore\ND_lab\A-diffusion\data\ct_shape_data\resample_512\final_contours"
    final_contour_output_folder = r"E:\MyStore\ND_lab\A-diffusion\data\ct_shape_data\resample_512\final_contours_v3"

    for caseID in range(centerlines.shape[0]):
        centerline = centerlines[caseID]
        ct_volume = ct_list[caseID]
        # ct_volume = np.clip(ct_volume, 0, 500)
        origin = origin_list[caseID]
        spacing = spacing_list[caseID]
        slices = []
        normal1_list = []
        normal2_list = []
        physical_coords_list = []
        for i in range(centerline.shape[0]):
            # Step 1: Compute tangent vector
            if i == centerline.shape[0] - 1:  # Last point
                tangent = centerline[i] - centerline[i - 1]
            else:
                tangent = centerline[i + 1] - centerline[i]
            tangent = tangent / np.linalg.norm(tangent)  # Normalize

            # Step 2: Find two orthogonal vectors to define the plane
            # Use any vector not collinear with tangent, here [0, 1, 0] as an example
            arbitrary_vec = np.array([0, 1, 0])
            if np.allclose(
                    tangent,
                    arbitrary_vec):  # if collinear, change arbitrary vector
                arbitrary_vec = np.array([1, 0, 0])
            normal1 = np.cross(tangent, arbitrary_vec)
            normal1 = normal1 / np.linalg.norm(normal1)
            normal2 = np.cross(tangent, normal1)
            normal2 = normal2 / np.linalg.norm(normal2)
            normal1_list.append(normal1)
            normal2_list.append(normal2)

            # Step 3: Define the 2D grid in the plane
            grid_size = 128  # Define size of slice in pixels
            # bound = 512 * spacing[0] + origin[0]  # Define the extent of the slice in mm
            bound = 8

            u = np.linspace(-bound / 2, bound / 2, grid_size)
            v = np.linspace(-bound / 2, bound / 2, grid_size)
            # u = np.linspace(-grid_size / 2, grid_size / 2, grid_size)
            # v = np.linspace(-grid_size / 2, grid_size / 2, grid_size)
            U, V = np.meshgrid(u, v)

            # Convert to 3D coordinates in the volume
            slice_coords = centerline[
                i] + U[:, :, None] * normal1 + V[:, :, None] * normal2
            physical_coords = slice_coords.copy()
            physical_coords_list.append(physical_coords)
            slice_coords = (slice_coords - origin) / spacing
            # slice_coords = slice_coords.astype(int)

            # Step 4: Sample the CT volume using interpolation
            # Extract x, y, z coordinates for interpolation
            x, y, z = slice_coords[..., 0], slice_coords[...,
                                                         1], slice_coords[...,
                                                                          2]

            # Interpolate the CT volume at these points
            slice_data = map_coordinates(
                ct_volume,
                [x.ravel(), y.ravel(), z.ravel()], order=1)
            slice_data = slice_data.reshape((grid_size, grid_size))

            slices.append(slice_data)

        # =====================export 2D slices as PNG=========================
        # # os.makedirs(f"{output_folder}/{caseID + 1}", exist_ok=True)
        # for idx, slice_data in enumerate(slices):
        #     plt.imshow(slice_data, cmap="gray")
        #     plt.axis("off")  
        #     # plt.savefig(f"{output_folder}/{caseID + 1}/slice_{idx:02d}.png", bbox_inches="tight", pad_inches=0)
        #     plt.show()
        # #     plt.close()

        # =====================get segmentation=========================
        masks = []
        for slice in slices:
            # plt.imshow(slice, cmap="gray")
            # plt.show()
            slice = torch.from_numpy(slice).unsqueeze(0).unsqueeze(
                0).cuda()  # Add batch and channel dimensions
            slice = (slice - slice.min()) / (slice.max() - slice.min()
                                             )  # Normalize to [0, 1]
            point_coords = torch.Tensor([
                slice.shape[2] // 2, slice.shape[3] // 2
            ]).unsqueeze(0).unsqueeze(0).cuda()  # Example point coordinates
            # point_coords2 = torch.Tensor([slice.shape[2] // 2 - 15, slice.shape[3] // 2]).unsqueeze(0).unsqueeze(
            #     0).cuda()  # Example point coordinates
            # point_coords3 = torch.Tensor([slice.shape[2] // 2 + 15, slice.shape[3] // 2]).unsqueeze(0).unsqueeze(
            #     0).cuda()
            # point_coords4 = torch.Tensor([slice.shape[2] // 2, slice.shape[3] // 2 + 15]).unsqueeze(0).unsqueeze(
            #     0).cuda()
            # point_coords5 = torch.Tensor([slice.shape[2] // 2, slice.shape[3] // 2 - 15]).unsqueeze(0).unsqueeze(
            #     0).cuda()
            # point_coords = torch.cat((point_coords, point_coords2, point_coords3, point_coords4, point_coords5), dim=1)
            point_labels = torch.Tensor(
                [1]).unsqueeze(0).cuda()  # Example point labels
            # point_labels = torch.cat((point_labels, point_labels, point_labels, point_labels, point_labels), dim=1)
            # Use ScribblePromptSAM to get segmentation
            sp_sam = ScribblePromptSAM()
            mask, img_features, low_res_logits = sp_sam.predict(
                slice,  # (B, 1, H, W)
                point_coords,  # (B, n, 2)
                point_labels  # (B, n)
            )  # -> (B, 1, H, W), (B, 16, 256, 256), (B, 1, 256, 256)
            # display the mask
            # plt.imshow(mask[0, 0].cpu().numpy(), cmap="gray")
            # plt.axis("off")
            # plt.show()

            plt.subplot(1, 2, 1)
            plt.imshow(slice[0, 0].cpu().numpy() * 255, cmap='gray')
            plt.title('CT Slice')
            # plt.axis('off')

            plt.subplot(1, 2, 2)
            plt.imshow(slice[0, 0].cpu().numpy() * 255, cmap='gray')
            plt.imshow(mask[0, 0].cpu().numpy(), cmap='jet', alpha=0.5)
            plt.title('CT with Segmentation Mask')
            plt.scatter(point_coords.cpu().numpy().reshape(-1, 2)[:, 1],
                        point_coords.cpu().numpy().reshape(-1, 2)[:, 0],
                        c='red',
                        s=10)
            plt.axis('off')

            plt.show()

            mask = mask[0, 0].cpu().numpy()
            masks.append(mask)

        # =====================find contours==========================
        all_contours_in_physical_space = []

        for i, segmented_slice in enumerate(masks):
            threshold = 0.3
            segmented_slice = (segmented_slice >= threshold).astype(
                np.uint8) * 255
            kernel = np.ones((7, 7), np.uint8)
            segmented_slice = cv2.morphologyEx(segmented_slice,
                                               cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(segmented_slice.astype(np.uint8),
                                           cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_NONE)

            segmented_slice_color = cv2.cvtColor(segmented_slice,
                                                 cv2.COLOR_GRAY2BGR)
            # cv2.drawContours(segmented_slice_color, contours, -1, (0, 0, 255), 5)  # TODO: Draw contours on the mask
            # cv2.imshow("Contours", segmented_slice_color)
            # cv2.waitKey(0)

            contour = np.concatenate(contours, axis=0)  # nx1x2
            contour = contour[:, 0, :]  # nx2
            center = np.array(
                [segmented_slice.shape[1] // 2, segmented_slice.shape[0] // 2])
            contour = sort_contours(
                contour, center)  # TODO: make the contours in the sorted order
            contour = downsample_contour(contour, num_points=32)

            single_mask_contour_coord = []

            for point in contour:
                x_pixel, y_pixel = point

                physical_point = physical_coords_list[i][int(y_pixel),
                                                         int(x_pixel)]
                single_mask_contour_coord.append(physical_point)  # nx3

            all_contours_in_physical_space.append(
                np.array(single_mask_contour_coord))  # 16xnx3

        # display the contours
        plotter = pv.Plotter()
        for i in range(len(all_contours_in_physical_space)):
            plotter.add_points(all_contours_in_physical_space[i],
                               render_points_as_spheres=True,
                               point_size=10)
        plotter.show()

        # # =====================smooth contours==========================
        # all_contours_in_physical_space = np.array(all_contours_in_physical_space)
        # all_contours_in_physical_space = smooth(all_contours_in_physical_space, centerline)
        # # display the contours
        # plotter = pv.Plotter()
        # for i in range(len(all_contours_in_physical_space)):
        #     plotter.add_points(all_contours_in_physical_space[i], render_points_as_spheres=True, point_size=10)
        # plotter.show()

        # export 3D contours npy file
        final_contour_result = []
        for i in range(len(all_contours_in_physical_space)):
            slice_result = np.expand_dims(all_contours_in_physical_space[i],
                                          0)  # 1 x n x 3
            final_contour_result.append(slice_result)
        final_contour_result = np.concatenate(final_contour_result,
                                              axis=0)  # 16 x n x 3
        np.save(
            os.path.join(final_contour_output_folder,
                         f"contours_case_{caseID + 1}.npy"),
            final_contour_result)

        print("所有轮廓的物理空间坐标已计算完成！")
        # break # TODO: quick test


if __name__ == '__main__':
    main()
