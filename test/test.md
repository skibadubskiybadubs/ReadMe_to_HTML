# Header 1
sometext <br />
<img src="https://github.com/user-attachments/assets/b976db6b-364b-429c-a278-948689419871" width="400"> <br />

## Header 2
- **Parallel Processing**: Automatically detects available CPU cores and runs multiple simulations concurrently
- **Real-time Monitoring**: Live UI showing simulation progress, CPU and memory usage
- **Automatic Staging**: Queues simulations and starts new ones as others complete
- **Error Handling**: Detects and reports simulation failures in real-time
- **CSV Reporting**: Generates a detailed CSV report of all simulation runs
- **Resource Management**: Monitors and displays CPU and memory usage for each simulation

### Header 3
> **Boiler:** x3 Electric <br />
> **Capacity (kW):** Multiple units: 4.5kW for larger units, 1.5kW for common areas <br />
> **Efficiency:** Not specified <br />
> ![image](https://github.com/user-attachments/assets/f53fbe8d-e98a-4998-a848-3a46def6528b) <br />
> Tank Volume (Storage Capacity): (55+37+6)*0.00378541 = 0.37097 <br />
> The schedule says **typical for ..**, which means there are not just 3 boilers, but one per suite of a type <br />
> Sum up and model the DHW Storage Capacity (Tank Volume) and Heating Capacity (W) per the mech schedule. <br />
> Looks like there are many small ones in the suites, and maybe 1 more for the amenities. <br />
> 55gals = 0.208198m3; 37gals = 0.14006m3; 6gals = 0.0227125m3. <br />

| **Space**      | **Count** | **Storage Capacity** | **Heating Capacity** |
|----------------|-----------|----------------------|-----------------------|
| Suite 1 bd     | 37        | 5.18222              | 166,500               |
| Suite 2+ bd    | 23        | 4.788554             | 103,500               |
| Amenities      | 1         | 0.0227125            | 1,500                 |

> ![image](https://github.com/user-attachments/assets/4f1116fd-15c2-404f-a86a-3d2eb318502c)

#### Header 4
1. Clone this repository:
   ```bash
   git clone https://github.com/skibadubskiybadubs/energyplus_multiprocessing.git
   cd energyplus-parallel
   ```

2. Install the required dependencies:
   ```bash
   pip install rich psutil
   ```

- `--eplus`: Path to the EnergyPlus installation directory (required)
- `--max-workers`: Maximum number of parallel simulations (default: number of logical processors - 1)
- `--csv`: Output CSV file name (default: "simulation_results.csv")

##### Header 5
1. **Error: EnergyPlus executable not found**
   - Ensure the path to EnergyPlus is correct
   - Verify EnergyPlus is properly installed

2. **Simulations start but fail immediately**
   - Check that your IDF files are valid
   - Verify that the weather file is in the same directory

3. **Script crashes with memory errors**
   - Reduce the number of parallel simulations using the `--max-workers` option