from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import nibabel as nib
import numpy as np
import pyvista as pv
from scipy import ndimage


def load_nii_volume(path: str | Path) -> tuple[np.ndarray, tuple[float, float, float], np.ndarray]:
    """Load a NIfTI file and return volume data, voxel spacing, and origin."""
    nii = nib.load(str(path))
    data = nii.get_fdata()
    spacing = tuple(float(v) for v in nii.header.get_zooms()[:3])
    origin = nii.affine[:3, 3]
    return data, spacing, origin


def extract_isosurface(
    volume: np.ndarray,
    spacing: tuple[float, float, float],
    origin: np.ndarray,
    *,
    threshold: float = 0.5,
    sigma: float = 1.0,
    smooth_iter: int = 50,
    smooth_relax: float = 0.1,
) -> Optional[pv.PolyData]:
    """Create a mesh via marching cubes with optional Gaussian smoothing."""
    field = volume.astype(float)
    if sigma > 0:
        field = ndimage.gaussian_filter(field, sigma=sigma)

    grid = pv.ImageData(dimensions=field.shape, spacing=spacing, origin=origin)
    grid.point_data["values"] = field.flatten(order="F")
    surface = grid.contour(isosurfaces=[threshold], scalars="values")

    if surface.n_points == 0:
        return None
    if smooth_iter > 0:
        surface = surface.smooth(n_iter=int(smooth_iter), relaxation_factor=smooth_relax)
    return surface


def extract_label_meshes(
    volume: np.ndarray,
    labels: list[float] | tuple[float, ...],
    spacing: tuple[float, float, float],
    origin: np.ndarray,
    *,
    sigma: float = 1.0,
    smooth_iter: int = 50,
    smooth_relax: float = 0.1,
    threshold: float = 0.5,
) -> list[tuple[float, pv.PolyData]]:
    """Extract meshes for multiple labels (mask==label) for single-shot visualization."""
    meshes: list[tuple[float, pv.PolyData]] = []
    for lbl in labels:
        mask = (volume == lbl).astype(float)
        mesh = extract_isosurface(
            mask,
            spacing,
            origin,
            threshold=threshold,
            sigma=sigma,
            smooth_iter=smooth_iter,
            smooth_relax=smooth_relax,
        )
        if mesh is not None:
            meshes.append((lbl, mesh))
    return meshes


def _set_view(plotter: pv.Plotter, view: str) -> None:
    bounds = plotter.bounds
    x_mid = 0.5 * (bounds[0] + bounds[1])
    y_mid = 0.5 * (bounds[2] + bounds[3])
    z_mid = 0.5 * (bounds[4] + bounds[5])
    span = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4], 1.0)
    dist = span * 1.8

    if view == "iso":
        plotter.view_isometric()
        return

    if view == "left":
        position = (x_mid - dist, y_mid, z_mid)
        up = (0, 0, 1)
    elif view == "right":
        position = (x_mid + dist, y_mid, z_mid)
        up = (0, 0, 1)
    elif view == "top":
        position = (x_mid, y_mid, z_mid + dist)
        up = (0, 1, 0)
    elif view == "front":
        position = (x_mid, y_mid - dist, z_mid)
        up = (0, 0, 1)
    else:
        plotter.view_isometric()
        return

    plotter.camera_position = [position, (x_mid, y_mid, z_mid), up]


def visualize_mesh(
    mesh: pv.PolyData,
    *,
    color: str = "#4C78A8",
    background: str = "white",
    view: str = "iso",
    screenshot: str | Path | None = None,
    show_edges: bool = False,
) -> Optional[str]:
    """Render a mesh in PyVista; optionally return a saved screenshot path."""
    off_screen = screenshot is not None
    plotter = pv.Plotter(off_screen=off_screen, window_size=(1024, 768))
    plotter.set_background(background)
    plotter.add_mesh(
        mesh,
        color=color,
        show_edges=show_edges,
        smooth_shading=True,
        specular=0.15,
        specular_power=5,
        ambient=0.3,
        diffuse=0.6,
    )
    plotter.add_axes()
    _set_view(plotter, view)

    if screenshot:
        screenshot_path = str(screenshot)
        plotter.show(screenshot=screenshot_path, auto_close=True)
        return screenshot_path

    plotter.show()
    return None


def visualize_meshes(
    meshes: list[tuple[pv.PolyData, str]],
    *,
    background: str = "white",
    view: str = "iso",
    screenshot: str | Path | None = None,
    show_edges: bool = False,
) -> Optional[str]:
    """Render multiple meshes at once (mesh, color) tuples."""
    off_screen = screenshot is not None
    plotter = pv.Plotter(off_screen=off_screen, window_size=(1200, 800))
    plotter.set_background(background)

    for mesh, color in meshes:
        plotter.add_mesh(
            mesh,
            color=color,
            show_edges=show_edges,
            smooth_shading=True,
            specular=0.15,
            specular_power=5,
            ambient=0.3,
            diffuse=0.6,
        )
    plotter.add_axes()
    _set_view(plotter, view)

    if screenshot:
        screenshot_path = str(screenshot)
        plotter.show(screenshot=screenshot_path, auto_close=True)
        return screenshot_path

    plotter.show()
    return None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load a NIfTI volume, extract a marching-cubes mesh, and visualize it with PyVista.",
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=Path,
        help="Path to .nii or .nii.gz file.",
    )
    parser.add_argument(
        "--label",
        type=float,
        help="If set, extract the isosurface of this label value (uses mask==label and threshold=0.5).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Iso-value used when --label is not provided (default: 0.5).",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=1.0,
        help="Gaussian smoothing sigma before marching cubes (default: 1.0).",
    )
    parser.add_argument(
        "--smooth-iter",
        type=int,
        default=50,
        help="Number of smoothing iterations on the mesh (default: 50).",
    )
    parser.add_argument(
        "--smooth-relax",
        type=float,
        default=0.1,
        help="Relaxation factor for mesh smoothing (default: 0.1).",
    )
    parser.add_argument(
        "--color",
        default="#4C78A8",
        help="Mesh color for visualization (default: #4C78A8).",
    )
    parser.add_argument(
        "--background",
        default="white",
        help="Background color for visualization (default: white).",
    )
    parser.add_argument(
        "--view",
        default="iso",
        choices=["iso", "left", "right", "top", "front"],
        help="Camera preset for quick orientation (default: iso).",
    )
    parser.add_argument(
        "--screenshot",
        type=Path,
        help="If set, render off-screen and save a screenshot to this path.",
    )
    parser.add_argument(
        "--show-edges",
        action="store_true",
        help="Draw triangle edges on the mesh.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    volume, spacing, origin = load_nii_volume(args.input)

    if args.label is not None:
        field = (volume == args.label).astype(float)
        isovalue = 0.5
    else:
        field = volume
        isovalue = args.threshold

    mesh = extract_isosurface(
        field,
        spacing,
        origin,
        threshold=isovalue,
        sigma=args.sigma,
        smooth_iter=args.smooth_iter,
        smooth_relax=args.smooth_relax,
    )

    if mesh is None:
        raise SystemExit(
            f"No surface extracted from {args.input} at threshold {isovalue}. "
            "Try a different label/threshold or lower sigma."
        )

    screenshot_path = visualize_mesh(
        mesh,
        color=args.color,
        background=args.background,
        view=args.view,
        screenshot=args.screenshot,
        show_edges=args.show_edges,
    )

    if screenshot_path:
        print(f"Saved screenshot to {screenshot_path}")


if __name__ == "__main__":
    main()
