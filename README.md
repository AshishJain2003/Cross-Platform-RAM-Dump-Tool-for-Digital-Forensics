# Cross-Platform RAM Dump Collection Tool

<div align="center">
  <a href="https://license-instructions.netlify.app/" target="_blank">
    <img src="https://img.shields.io/badge/🚨-READ%20BEFORE%20FORKING-red?style=for-the-badge&labelColor=darkred" alt="Read Before Forking">
  </a>
</div>

This tool facilitates the collection of RAM dumps on both Windows and Linux (ParrotOS, Kali). The collected RAM dump can be analyzed using tools like **Volatility** to extract process IDs and other forensic data.

---

## Features
- **Windows Support**: Seamless RAM acquisition using Python and Winpmem.
- **Linux Support**: RAM dumping through LiME kernel module integrated with Python.
- **Output**: Generates `.raw` format compatible with Volatility and other forensic tools.
- **Automation**: OS detection and tool execution handled automatically via Python subprocess.

---

## Prerequisites

### Common Requirements
- Python 3.6 or later
- Required privileges:
  - **Windows**: Administrator access
  - **Linux**: Root or `sudo` access

### Additional Requirements for Linux
- **lime.ko**: Must be compiled for your current kernel using the official LiME source.

---

## Usage Instructions

### **For Windows**
1. Navigate to the `RAM Dumper` folder inside the project.
2. Open Command Prompt as **Administrator** in that directory.
3. Run the script using:
   ```bash
   python ram_dump.py
