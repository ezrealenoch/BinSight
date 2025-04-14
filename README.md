# BinSight: CAPA-Ollama-Ghidra Inspection Tool

BinSight is an integrated tool designed to enhance malware analysis by combining the capabilities of CAPA (Common Automated Platform for Analyzing Malware), a locally hosted Ollama Large Language Model (LLM), and the Ghidra reverse engineering framework.

## Overview

BinSight streamlines the malware analysis workflow by:
- Processing CAPA output files to extract rule matches and their addresses
- Assisting navigation to these addresses within Ghidra
- Leveraging a local Ollama LLM to provide contextual analysis of code segments
- Maintaining data privacy through local analysis without sending data to external services

## Features

- **CAPA Integration**: Load and parse CAPA output files (JSON format)
- **Ghidra Navigation Assistance**: Easily copy addresses and follow guided instructions to locate them in Ghidra
- **Ollama LLM Integration**: Send code snippets from Ghidra to your local Ollama instance for AI-powered analysis
- **Configuration Management**: Configure connection details for your Ollama LLM and Ghidra installation
- **User-Friendly Interface**: Intuitive UI with clear workflow from CAPA findings to Ollama analysis

## Requirements

- Python 3.6+
- PyQt5
- Requests library
- Local Ollama instance with a compatible model (e.g., llama3)
- Ghidra installation (for reverse engineering, not directly integrated)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ezrealenoch/BinSight.git
cd BinSight
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start your local Ollama instance (typically runs at http://localhost:11434)

## Usage

1. Run the application from the project root directory:
```bash
python -m src.main
```

2. Configure Ollama and Ghidra paths:
   - Click on `File > Configure`
   - Enter your Ollama API URL (e.g., `http://localhost:11434`)
   - Specify your Ghidra installation directory (optional)
   - Click OK to save

3. Load a CAPA output file:
   - Click on `File > Load CAPA File...`
   - Select a CAPA JSON output file

4. Analyze with Ghidra and Ollama:
   - Select an address from the CAPA findings tree
   - Use the "Copy Address" button and follow the Ghidra navigation instructions
   - After navigating to the address in Ghidra, copy the relevant code
   - Paste the code into BinSight's "Paste Ghidra Code" area
   - Enter a prompt for the Ollama LLM
   - Click "Analyze with Ollama"

5. View results:
   - Analysis results from Ollama will be displayed in the Results tab

## Workflow

The typical workflow is:

1. Run CAPA on your malware sample (outside of this tool)
2. Load the CAPA output into BinSight
3. Use BinSight to navigate to addresses of interest in Ghidra
4. Send code snippets to Ollama for contextual analysis
5. Interpret results to gain deeper understanding of the malware

## License

[Include license information here]

## Acknowledgments

- [CAPA](https://github.com/mandiant/capa) by Mandiant for malware capability analysis
- [Ollama](https://github.com/ollama/ollama) for local LLM hosting
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra) by NSA for reverse engineering 