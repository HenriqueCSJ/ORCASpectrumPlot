import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from scipy.signal import convolve, gaussian
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Initialize the global spectrum_data with an empty DataFrame
spectrum_data = pd.DataFrame()


# Function to convolve with Gaussian
def convolve_with_gaussian(energy, intensity, fwhm):
    sigma = fwhm / np.sqrt(8 * np.log(2))
    n_points = int(fwhm * 10)
    gaussian_kernel = gaussian(n_points, sigma)
    gaussian_kernel /= gaussian_kernel.sum()
    convolved_intensity = convolve(intensity, gaussian_kernel, mode="same")
    return convolved_intensity


# Function to update plot
def update_plot(fwhm, max_energy, shift=0):
    global spectrum_data
    # Only update the plot if data is loaded
    if not spectrum_data.empty:
        # Apply the energy shift
        shifted_energy = spectrum_data["Energy"] + shift

        # Sort the spectrum data by energy in ascending order if needed
        sorted_indices = shifted_energy.argsort()
        shifted_energy = shifted_energy.iloc[sorted_indices]
        sorted_intensity = spectrum_data["TotalSpectrum"].iloc[sorted_indices]

        convolved = convolve_with_gaussian(shifted_energy, sorted_intensity, fwhm)
        convolved *= sorted_intensity.max() / convolved.max()

        # Filter the data based on the maximum energy range
        mask = shifted_energy <= max_energy
        filtered_spectrum = shifted_energy[mask]
        filtered_convolved = convolved[mask]

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
        ax.set_title("Spectrum Convolution with Gaussian Function")
        ax.set_xlabel("Energy (nm)")
        ax.set_ylabel("Intensity")
        ax.set_xlim(filtered_spectrum.min(), max_energy)
        ax.legend()
        ax.grid(True)
        canvas.draw()


# Function to load data
def load_data():
    global spectrum_data
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            spectrum_data = pd.read_csv(
                file_path,
                delim_whitespace=True,
                usecols=[0, 1],
                names=["Energy", "TotalSpectrum"],
            )
            spectrum_data["Energy"] = pd.to_numeric(
                spectrum_data["Energy"], errors="coerce"
            )
            spectrum_data["TotalSpectrum"] = pd.to_numeric(
                spectrum_data["TotalSpectrum"], errors="coerce"
            )
            spectrum_data.dropna(inplace=True)
            spectrum_data.sort_values("Energy", inplace=True)

            # Update the maximum energy slider range based on the loaded data
            max_energy_scale.config(
                from_=spectrum_data["Energy"].min(), to=spectrum_data["Energy"].max()
            )
            max_energy_scale.set(spectrum_data["Energy"].max())
            shift_scale.config(from_=-max_energy_scale.get(), to=max_energy_scale.get())
            shift_scale.set(0)  # Reset shift to zero
            fwhm_scale.config(state="normal")
            max_energy_scale.config(state="normal")
            shift_scale.config(state="normal")

            # Update the plot with the new data and current FWHM value
            update_plot(fwhm_scale.get(), max_energy_scale.get(), shift_scale.get())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
    else:
        messagebox.showinfo("Load Data", "No file selected.")


# Function to save data
def save_data():
    fwhm = fwhm_scale.get()
    max_energy = max_energy_scale.get()
    shift = shift_scale.get()
    shifted_energy = spectrum_data["Energy"] + shift
    convolved = convolve_with_gaussian(
        shifted_energy, spectrum_data["TotalSpectrum"], fwhm
    )
    convolved *= spectrum_data["TotalSpectrum"].max() / convolved.max()
    mask = shifted_energy <= max_energy
    filtered_spectrum = shifted_energy[mask]
    filtered_convolved = convolved[mask]
    save_df = pd.DataFrame(
        {
            "ShiftedEnergy": filtered_spectrum,
            "TotalSpectrum": spectrum_data["TotalSpectrum"][mask],
            "ConvolvedSpectrum": filtered_convolved,
        }
    )
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
    )
    if file_path:  # Check if a file path was provided
        save_df.to_csv(file_path, index=False)
        messagebox.showinfo(
            "Save Data", "The convolved spectrum data has been saved successfully."
        )


# Create the main window
root = tk.Tk()
root.title("Spectrum Analyzer")

# Create a frame for the Matplotlib plot
plot_frame = tk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=1)

# Create the matplotlib figure and axes
fig, ax = plt.subplots(figsize=(10, 5))
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

# Create a toolbar frame
toolbar_frame = tk.Frame(root)
toolbar_frame.pack(fill=tk.X)

# Add buttons
load_button = tk.Button(toolbar_frame, text="Load Data", command=load_data)
load_button.pack(side=tk.LEFT, padx=2)

save_button = tk.Button(toolbar_frame, text="Save Data", command=save_data)
save_button.pack(side=tk.LEFT, padx=2)

# Create an FWHM scale slider
fwhm_scale = tk.Scale(
    toolbar_frame,
    from_=0.1,
    to=200,
    resolution=0.1,
    orient=tk.HORIZONTAL,
    label="FWHM",
    command=lambda v: update_plot(float(v), max_energy_scale.get(), shift_scale.get()),
)
fwhm_scale.set(1.0)  # Default FWHM value
fwhm_scale.pack(side=tk.LEFT, fill=tk.X, expand=1)
fwhm_scale.config(state="disabled")  # Disable the slider initially

# Create a maximum energy scale slider
max_energy_scale = tk.Scale(
    toolbar_frame,
    from_=0,
    to=2000,
    resolution=1,
    orient=tk.HORIZONTAL,
    label="Max Energy",
    command=lambda v: update_plot(fwhm_scale.get(), float(v), shift_scale.get()),
)
max_energy_scale.set(1000)  # Set the default value for the max energy slider
max_energy_scale.pack(side=tk.LEFT, fill=tk.X, expand=1)
max_energy_scale.config(state="disabled")  # Disable the slider initially

# Create an energy shift scale slider
shift_scale = tk.Scale(
    toolbar_frame,
    from_=-1000,
    to=1000,
    resolution=1,
    orient=tk.HORIZONTAL,
    label="Energy Shift (nm)",
    command=lambda v: update_plot(fwhm_scale.get(), max_energy_scale.get(), float(v)),
)
shift_scale.set(0)  # Default shift value
shift_scale.pack(side=tk.LEFT, fill=tk.X, expand=1)
shift_scale.config(state="disabled")  # Disable initially

# Start the Tkinter loop
root.mainloop()
