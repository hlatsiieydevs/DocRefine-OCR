# Foundation Setup Guide (WSL2 & Anaconda)

This guide covers the one-time setup required on your Windows 10/11 machine to prepare it for advanced Python and AI development.

## Step 1: Install WSL2 (Windows Subsystem for Linux)
We will install Ubuntu, a popular version (distribution) of Linux, right inside your Windows machine.

1. Open your Windows **Start Menu**, search for **PowerShell**.
2. Right-click on "Windows PowerShell" and select **"Run as Administrator"**.
3. In the blue window, copy and paste this exact command, then press Enter:
   ```powershell
   wsl --install
   ```
4. Wait for it to finish downloading and installing.
5. **Restart your computer.**
6. When you log back in, a black window should appear automatically asking you to create a **UNIX username** and **password**. (Note: when typing your password, no characters will show up on screen. This is a normal security feature. Just type it and press Enter).

*You now have a fully functional Linux terminal! You can always open it by searching for "Ubuntu" in your Windows Start Menu.*

## Step 2: Install Anaconda (Python Package Manager)
Anaconda is an industry-standard tool for managing Python programming packages. Sometimes different projects need different versions of Python or libraries. Anaconda keeps them neatly separated in isolated "environments."

1. Open your **Ubuntu** application from the Windows Start Menu.
2. Download the Anaconda installer by running:
   ```bash
   wget https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh
   ```
3. Run the installer:
   ```bash
   bash Anaconda3-2024.02-1-Linux-x86_64.sh
   ```
4. Press **Enter** to read the license, and hold down **Space** to scroll to the bottom. Type `yes` to accept.
5. Press **Enter** to confirm the installation location. 
6. When it asks if you wish the installer to initialize Anaconda3 by running conda init, type `yes`.
7. Close the Ubuntu window and open a fresh one to apply the changes.
8. You should now see `(base)` next to your username in the terminal.

## Step 3: Install Base Packages & Jupyter Notebook
Jupyter Notebook is a popular interactive coding environment. It's the standard tool used by data scientists.

1. In your **Ubuntu** terminal, run the following command to make sure Anaconda is fully updated:
   ```bash
   conda update -n base -c defaults conda -y
   ```
2. While we will install project-specific packages during the main README setup, it's good to have standard Jupyter available generally:
   ```bash
   conda install -c conda-forge jupyterlab notebook -y
   ```

**You are now ready!** Head back to the main [README.md](../../README.md) to continue setting up the project.
