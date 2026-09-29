"""
Quick-look plot of average counts vs stepper-table step and azimuth bin,
read directly from an L1 EEA CDF file.
"""
import argparse

import matplotlib.pyplot as plt
import numpy as np
from spacepy import pycdf

from hermes_eea.io.EEA import REAL4FILL


def load_avg_skymap(cdf_path):
    """
    Average `hermes_eea_accum` over all sweeps, dropping the MAX_STEPS
    fill-value padding (steps beyond the stepper table's real length).

    Returns
    -------
    avg_counts : ndarray, shape (n_real_steps, N_AZIMUTH)
    """
    with pycdf.CDF(str(cdf_path)) as cdf:
        accum = np.array(cdf["hermes_eea_accum"][:])  # (n_sweeps, MAX_STEPS, N_AZIMUTH)
        energies = np.array(cdf["hermes_eea_energy_profile"][0])  # (MAX_STEPS,)

    n_real_steps = int(np.sum(energies != REAL4FILL))
    accum = accum[:, :n_real_steps, :]
    accum = np.where(accum == REAL4FILL, np.nan, accum)  # last, incomplete sweep may still hold fill
    avg_counts = np.nanmean(accum, axis=0)  # (n_real_steps, N_AZIMUTH)
    return avg_counts


def plot_avg_skymap(cdf_path, out_path=None):
    avg_counts = load_avg_skymap(cdf_path)

    fig, ax = plt.subplots(figsize=(9, 5))
    # transpose so steps are on x, azimuth bin is on y (matching the reference plot orientation)
    im = ax.imshow(
        avg_counts.T,
        origin="lower",
        aspect="auto",
        cmap="nipy_spectral",
        extent=[0, avg_counts.shape[0], 0, avg_counts.shape[1]],
    )
    ax.set_xlabel("Stepper Table Steps")
    # no physical degree calibration for azimuth exists in this repo yet, so we plot bin index
    ax.set_ylabel("Azimuth Bin Index")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Avg Counts")
    fig.tight_layout()

    if out_path:
        fig.savefig(out_path, dpi=150)
        print(f"Saved plot to {out_path}")
    return fig, ax


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cdf_path")
    parser.add_argument("-o", "--out", default=None, help="Path to save the plot (e.g. skymap.png)")
    args = parser.parse_args()
    plot_avg_skymap(args.cdf_path, args.out)
    if not args.out:
        plt.show()
