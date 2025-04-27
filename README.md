# Math Trainer

## CLI Tools

This project provides two CLI tools: `addsub` and `mathrally`. Both tools allow generating exercises or rallies in SVG and/or PDF formats.

### Common Options

Both `addsub` and `mathrally` support the following common options:

- `--output`: Specifies the output file name for the SVG file.
- `--format`: Specifies the output format. Options are:
  - `svg`: Generates only the SVG file.
  - `pdf`: Generates only the PDF file. In this case, a temporary SVG file is created and removed after the PDF is generated.
  - `both` (default): Generates both SVG and PDF files.

---

### `addsub` Command

The `addsub` command generates addition and subtraction exercises.

#### Usage

```bash
python cli/addsub.py --output <output_file> --format <format>
```

#### Example

1. Generate only an SVG file:
   ```bash
   python cli/addsub.py --output exercises.svg --format svg
   ```

2. Generate only a PDF file:
   ```bash
   python cli/addsub.py --output exercises.svg --format pdf
   ```

3. Generate both SVG and PDF files:
   ```bash
   python cli/addsub.py --output exercises.svg --format both
   ```

---

### `mathrally` Command

The `mathrally` command generates a math rally.

#### Usage

```bash
python cli/mathrally.py --output <output_file> --solution <solution_file> --format <format>
```

#### Example

1. Generate only SVG files:
   ```bash
   python cli/mathrally.py --output rally.svg --solution solution.svg --format svg
   ```

2. Generate only PDF files:
   ```bash
   python cli/mathrally.py --output rally.svg --solution solution.svg --format pdf
   ```

3. Generate both SVG and PDF files:
   ```bash
   python cli/mathrally.py --output rally.svg --solution solution.svg --format both
   ```

---

## Prerequisites

This project requires **Inkscape** for rendering SVG files to PDF. Ensure that Inkscape is installed and accessible via the command line.

### Installing Inkscape CLI

1. **Download and Install Inkscape**:
   - Visit the [Inkscape download page](https://inkscape.org/release/) and download the appropriate version for your operating system.
   - Follow the installation instructions for your platform.

2. **Verify Installation**:
   - Open a terminal or command prompt and run:
     ```bash
     inkscape --version
     ```
   - This should output the installed version of Inkscape. If the command is not recognized, ensure that Inkscape is added to your system's PATH.

3. **Add Inkscape to PATH (if necessary)**:
   - **Windows**:
     - Open the Start menu and search for "Environment Variables."
     - Edit the `Path` variable in the system variables section and add the directory where `inkscape.exe` is located (e.g., `C:\Program Files\Inkscape`).
   - **macOS/Linux**:
     - Add the Inkscape binary directory to your PATH. For example, add the following line to your `~/.bashrc` or `~/.zshrc` file:
       ```bash
       export PATH="/Applications/Inkscape.app/Contents/MacOS:$PATH"
       ```
     - Reload your shell configuration:
       ```bash
       source ~/.bashrc  # or source ~/.zshrc
       ```

4. **Test Again**:
   - Run `inkscape --version` to confirm that Inkscape is properly installed and accessible.

---

### Troubleshooting

- If you encounter issues, refer to the [Inkscape documentation](https://inkscape.org/doc/) or check the [FAQs](https://inkscape.org/learn/faq/).

---

# Developer Guide

## Running Tests

To run the tests with pytest, use the following command:

```sh
pytest
```

Make sure you have pytest installed. You can install it using pip:

```sh
pip install pytest
```
