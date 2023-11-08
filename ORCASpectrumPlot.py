# Import necessary libraries
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from scipy.signal import convolve, gaussian
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Create an empty DataFrame to store spectrum data
spectrum_data = pd.DataFrame()


# Define a function to convolve a spectrum with a Gaussian function
def convolve_with_gaussian(energy, intensity, fwhm):
    # Calculate the standard deviation (sigma) from FWHM
    sigma = fwhm / np.sqrt(8 * np.log(2))
    # Determine the number of points for the Gaussian kernel
    n_points = int(fwhm * 10)
    # Generate a Gaussian kernel
    gaussian_kernel = gaussian(n_points, sigma)
    gaussian_kernel /= gaussian_kernel.sum()
    # Convolve the intensity with the Gaussian kernel
    convolved_intensity = convolve(intensity, gaussian_kernel, mode="same")
    return convolved_intensity


# Define a function to update and plot the spectrum
def update_plot(fwhm, max_energy, shift=0, show_fc=False, show_ht=False):
    global spectrum_data
    if not spectrum_data.empty:
        # Shift the energy values by the specified amount
        shifted_energy = spectrum_data["Energy"] + shift
        # Sort the data by energy values
        sorted_indices = shifted_energy.argsort()
        shifted_energy = shifted_energy.iloc[sorted_indices]
        sorted_intensity = spectrum_data["TotalSpectrum"].iloc[sorted_indices]
        # Convolve the sorted intensity with a Gaussian
        convolved = convolve_with_gaussian(shifted_energy, sorted_intensity, fwhm)
        # Normalize the convolved spectrum
        convolved *= sorted_intensity.max() / convolved.max()
        # Apply a mask to limit the plotted energy range
        mask = shifted_energy <= max_energy
        filtered_spectrum = shifted_energy[mask]
        filtered_convolved = convolved[mask]
        # Clear the existing plot and create a new one
        ax.clear()
        ax.plot(
            filtered_spectrum,
            sorted_intensity[mask],
            label="Original Spectrum",
            color="blue",
        )
        ax.plot(
            filtered_spectrum,
            filtered_convolved,
            label="Convolved Spectrum",
            color="orange",
            linestyle="--",
        )
        if show_fc:
            sorted_intensity_fc = spectrum_data["IntensityFC"].iloc[sorted_indices]
            ax.plot(
                filtered_spectrum,
                sorted_intensity_fc[mask],
                label="IntensityFC",
                color="green",
                linestyle="-.",
            )
        if show_ht:
            sorted_intensity_ht = spectrum_data["IntensityHT"].iloc[sorted_indices]
            ax.plot(
                filtered_spectrum,
                sorted_intensity_ht[mask],
                label="IntensityHT",
                color="red",
                linestyle="-.",
            )
        ax.set_title("Spectrum Convolution with Gaussian Function")
        ax.set_xlabel("Energy (nm)")
        ax.set_ylabel("Intensity")
        ax.set_xlim(filtered_spectrum.min(), max_energy)
        ax.legend()
        ax.grid(True)
        canvas.draw()


# Define a function to load spectrum data from a file
def load_data():
    global spectrum_data
    # Open a file dialog to select a data file
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            # Read the data from the selected file
            spectrum_data = pd.read_csv(
                file_path,
                delim_whitespace=True,
                usecols=[0, 1, 2, 3],
                names=["Energy", "TotalSpectrum", "IntensityFC", "IntensityHT"],
            )
            # Convert columns to numeric values and handle NaN values
            spectrum_data["Energy"] = pd.to_numeric(
                spectrum_data["Energy"], errors="coerce"
            )
            spectrum_data["TotalSpectrum"] = pd.to_numeric(
                spectrum_data["TotalSpectrum"], errors="coerce"
            )
            spectrum_data["IntensityFC"] = pd.to_numeric(
                spectrum_data["IntensityFC"], errors="coerce"
            )
            spectrum_data["IntensityHT"] = pd.to_numeric(
                spectrum_data["IntensityHT"], errors="coerce"
            )
            spectrum_data.dropna(inplace=True)
            # Sort the data by energy values
            spectrum_data.sort_values("Energy", inplace=True)
            # Update scale ranges and enable UI elements
            max_energy_scale.config(
                from_=spectrum_data["Energy"].min(), to=spectrum_data["Energy"].max()
            )
            max_energy_scale.set(spectrum_data["Energy"].max())
            shift_scale.config(from_=-max_energy_scale.get(), to=max_energy_scale.get())
            shift_scale.set(0)
            fwhm_scale.config(state="normal")
            max_energy_scale.config(state="normal")
            shift_scale.config(state="normal")
            show_fc_button.config(state="normal")
            show_ht_button.config(state="normal")
            # Update the plot with initial settings
            update_plot(fwhm_scale.get(), max_energy_scale.get(), shift_scale.get())
        except Exception as e:
            # Show an error message if loading data fails
            messagebox.showerror("Error", f"Failed to load data: {e}")
    else:
        # Show an information message if no file is selected
        messagebox.showinfo("Load Data", "No file selected.")


# Define a function to save the convolved spectrum data to a file
def save_data():
    fwhm = fwhm_scale.get()
    max_energy = max_energy_scale.get()
    shift = shift_scale.get()
    show_fc = show_fc_var.get()
    show_ht = show_ht_var.get()

    shifted_energy = spectrum_data["Energy"] + shift
    sorted_indices = shifted_energy.argsort()
    shifted_energy = shifted_energy.iloc[sorted_indices]
    sorted_intensity = spectrum_data["TotalSpectrum"].iloc[sorted_indices]
    convolved = convolve_with_gaussian(shifted_energy, sorted_intensity, fwhm)
    convolved *= sorted_intensity.max() / convolved.max()
    mask = shifted_energy <= max_energy
    filtered_spectrum = shifted_energy[mask]
    filtered_convolved = convolved[mask]

    save_df = pd.DataFrame(
        {
            "ShiftedEnergy": filtered_spectrum,
            "TotalSpectrum": sorted_intensity[mask],
            "ConvolvedSpectrum": filtered_convolved,
        }
    )

    if show_fc:
        sorted_intensity_fc = spectrum_data["IntensityFC"].iloc[sorted_indices]
        save_df["IntensityFC"] = sorted_intensity_fc[mask]

    if show_ht:
        sorted_intensity_ht = spectrum_data["IntensityHT"].iloc[sorted_indices]
        save_df["IntensityHT"] = sorted_intensity_ht[mask]

    # Open a file dialog to specify the save location and filename
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
    )
    if file_path:
        # Save the convolved spectrum data to the selected file
        save_df.to_csv(file_path, index=False)
        # Show a success message
        messagebox.showinfo(
            "Save Data", "The convolved spectrum data has been saved successfully."
        )


# Create the main application window
root = tk.Tk()
root.title("Spectrum Analyzer")

# Create a frame for plotting
plot_frame = tk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=1)

# Create a Matplotlib figure and canvas for displaying the plot
fig, ax = plt.subplots(figsize=(10, 5))
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

# Create a frame for toolbar buttons
toolbar_frame = tk.Frame(root)
toolbar_frame.pack(fill=tk.X)

# Create buttons for loading and saving data
load_button = tk.Button(toolbar_frame, text="Load Data", command=load_data)
load_button.pack(side=tk.LEFT, padx=2)

save_button = tk.Button(toolbar_frame, text="Save Data", command=save_data)
save_button.pack(side=tk.LEFT, padx=2)

# Create scales and checkboxes for controlling the plot
fwhm_scale = tk.Scale(
    toolbar_frame,
    from_=0.1,
    to=200,
    resolution=0.1,
    orient=tk.HORIZONTAL,
    label="FWHM",
    command=lambda v: update_plot(
        float(v),
        max_energy_scale.get(),
        shift_scale.get(),
        show_fc_var.get(),
        show_ht_var.get(),
    ),
)
fwhm_scale.set(1.0)
fwhm_scale.pack(side=tk.LEFT, fill=tk.X, expand=1)
fwhm_scale.config(state="disabled")

max_energy_scale = tk.Scale(
    toolbar_frame,
    from_=0,
    to=2000,
    resolution=1,
    orient=tk.HORIZONTAL,
    label="Max Energy",
    command=lambda v: update_plot(
        fwhm_scale.get(),
        float(v),
        shift_scale.get(),
        show_fc_var.get(),
        show_ht_var.get(),
    ),
)
max_energy_scale.set(1000)
max_energy_scale.pack(side=tk.LEFT, fill=tk.X, expand=1)
max_energy_scale.config(state="disabled")

shift_scale = tk.Scale(
    toolbar_frame,
    from_=-1000,
    to=1000,
    resolution=1,
    orient=tk.HORIZONTAL,
    label="Energy Shift (nm)",
    command=lambda v: update_plot(
        fwhm_scale.get(),
        max_energy_scale.get(),
        float(v),
        show_fc_var.get(),
        show_ht_var.get(),
    ),
)
shift_scale.set(0)
shift_scale.pack(side=tk.LEFT, fill=tk.X, expand=1)
shift_scale.config(state="disabled")

show_fc_var = tk.BooleanVar()
show_fc_button = tk.Checkbutton(
    toolbar_frame,
    text="Show FC",
    variable=show_fc_var,
    state="disabled",
    command=lambda: update_plot(
        fwhm_scale.get(),
        max_energy_scale.get(),
        shift_scale.get(),
        show_fc_var.get(),
        show_ht_var.get(),
    ),
)
show_fc_button.pack(side=tk.LEFT, padx=2)

show_ht_var = tk.BooleanVar()
show_ht_button = tk.Checkbutton(
    toolbar_frame,
    text="Show HT",
    variable=show_ht_var,
    state="disabled",
    command=lambda: update_plot(
        fwhm_scale.get(),
        max_energy_scale.get(),
        shift_scale.get(),
        show_fc_var.get(),
        show_ht_var.get(),
    ),
)
show_ht_button.pack(side=tk.LEFT, padx=2)

# Start the Tkinter main event loop
root.mainloop()
