# Cross-Platform RAM Dump Collection Tool

<div align="center">
  <a href="https://license-instructions.netlify.app/" target="_blank">
    <img src="https://img.shields.io/badge/🚨-READ%20BEFORE%20FORKING-red?style=for-the-badge&labelColor=darkred" alt="Read Before Forking">
  </a>
</div>

This tool facilitates the collection of RAM dumps on both Windows and Linux (ParrotOS, Kali). The collected RAM dump can be analyzed using tools like **Volatility** to extract process IDs and other forensic data.

---

## Features
- **Windows Support**: Simplified execution using Python.
- **Linux Support**: Easily adaptable for ParrotOS and Kali Linux using the `lime.ko` module.
- **Output**: Generates `.raw` format for compatibility with forensic analysis tools.

---

## Prerequisites

### Common Requirements
- Python 3.6 or later.
- Necessary permissions:
  - **Windows**: Administrator privileges.
  - **Linux**: Root or `sudo` access.

### Additional Requirements for Linux
- **lime.ko**: Downloadable from the official Lime repository or through package managers.

---

## Usage Instructions

### **For Windows**
1. Navigate to the `RAM Dumper` folder in the tool's directory.
2. Open the terminal as **Administrator** in the same folder.
3. Execute the following command:
   ```bash
   python ram_dump.py
A `.raw` file containing the RAM dump will be generated in the same folder.

---

### **For Linux**

1. Before Running the Tool

- **Download the Lime kernel module (`lime.ko`):**
Use the following command to clone the Lime repository:

    ```bash
    sudo apt-get install -y linux-headers-$(uname -r) dkms git
    git clone https://github.com/504ensicsLabs/LiME
    cd LiME/src
    make

- The `lime.ko` file will be generated in the src directory.
Update the ram_dump.py file:
Replace the placeholder path in the following code:

     ```bash
        load_command = [
        "sudo",
        "insmod",
        "/lib/modules/6.10.11-amd64/updates/dkms/lime.ko",
        f"path={current_directory}/{MD5}/{MD5}.mem",
        "format=raw"
    ]
    
With the actual path to your downloaded `lime.ko` file. 
For example: `/path/to/your/lime.ko`
    
2. Running the Tool
- Navigate to the tool's directory where `ram_dump.py` is located.
Open a terminal and execute the following command:

    ```bash
    sudo python3 ram_dump.py
    
A `.raw` file containing the RAM dump will be created in the current directory.

3. Output Details
The tool generates a .raw file containing:
- Complete RAM dump of the system.
- Process IDs and other critical forensic information.
- The `.raw` file can be analyzed using forensic tools like Volatility for further investigation.

---

## Notes
1. Ensure the required permissions are granted before execution.
2. The tool is optimized for `Windows` and `Linux (ParrotOS, Kali)` but can be extended for other platforms with minor modifications.
3. For questions or issues, feel free to contact the project contributors.
4. For running this tool through `USB Drive`. Firstly your USB Drive should be empty and have storgae more than your computers physical memory. Now add `RAM Dumper` folder to your USB drive along with `autorun.INF` and `StartApp.bat` files into your USB drive and then then click on `StartApp.bat` file to start `RAM Dump tool`. After clicking it will ask for `run as administrator` two times. So, you have to allow and wait for some minutes your RAM Dump will be completed and will stored in your USB Drive.

---

## Thank you for using the Cross-Platform RAM Dump Collection Tool!
