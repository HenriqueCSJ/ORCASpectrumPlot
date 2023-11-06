# ORCASpectrumPlot Documentation

## Overview

ORCASpectrumPlot is a graphical user interface (GUI) tool developed to facilitate the loading, processing, and visualization of spectral data from `.spectrum` files, which are an output of the Excited State Dynamics (ESD) simulations performed with the ORCA quantum chemistry software package. This application provides features for spectral broadening through Gaussian convolution, energy domain shifting, and interactive visualization within specified energy ranges. It allows users to save their modified spectral data for further use.

## Requirements

- Python 3.x
- Libraries: `tkinter`, `pandas`, `scipy`, `matplotlib`, `numpy`

## Usage

1. **Load Data**: The application reads `.spectrum` files through the "Load Data" button, which imports the spectral data containing energy and intensity columns.

2. **Spectral Processing**: After loading the `.spectrum` file, the user can adjust the FWHM for Gaussian convolution, set the energy range for visualization, and shift the spectrum along the energy axis.

3. **Save Data**: The "Save Data" button allows the user to export the processed spectrum to a CSV file, retaining the applied Gaussian convolution and energy shifts.

## Features

- **Gaussian Convolution**: Applies a Gaussian convolution to the spectrum based on the user-defined FWHM value for spectral line broadening.
- **Energy Shift**: Enables shifting the spectral data along the energy axis by a user-defined value in nanometers.
- **Energy Range Selection**: Users can set an upper limit for energy values displayed in the spectrum.
- **Data Export**: Processed spectrum data can be saved in CSV format, which includes the energy shift and convolution adjustments.

## Interface Components

- **Load Data Button**: To load a `.spectrum` file.
- **Save Data Button**: To save the processed spectrum as a CSV file.
- **FWHM Slider**: To adjust the full width at half maximum for the Gaussian convolution.
- **Maximum Energy Slider**: To define the upper energy limit for the spectrum display.
- **Energy Shift Slider**: To apply an energy shift to the spectrum data.

## Default Values

- **Energy Units**: Nanometers (nm).
- **FWHM**: 1.0 nm (default starting value).
- **Max Energy**: Determined by the maximum energy in the loaded `.spectrum` file.
- **Energy Shift**: Initially set to 0 nm.

## Input File Format

The application expects `.spectrum` files that have a specific format:
- **First Column**: Energy in nanometers.
- **Second Column**: Spectral intensity.

Files should be plain text, with columns separated by whitespace, following the standard output format of ORCA's ESD module.

## Limitations

- The GUI is tailored for `.spectrum` files from ORCA's ESD code, and compatibility with other formats is not guaranteed.
- The GUI design adheres to the tkinter library's default aesthetics, which may not align with the visual themes of modern operating systems.

---
