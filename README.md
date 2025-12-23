# Accounting API Client

This tool automates the generation of invoices based on Upwork transaction CSV reports. It parses the CSV data, retrieves PDF summaries, and uses the InvoiceOcean API to issue invoices.

## Setup

### 1. Install Dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Configure Private Data
For security reasons, configuration and data files are kept in a separate `private_data` folder which is ignored by Git.

1.  Create a folder named `private_data` in the root directory.
2.  Create an empty file named `__init__.py` inside `private_data`.
3.  Copy `config.py.template` to `private_data/config.py` and fill in your API credentials and seller information.
4.  Place your `CustomerDatabase.xml` file inside `private_data/`.
5.  Place your Upwork transaction CSV files (e.g., `*_transaction_report.csv`) inside `private_data/`.

### 3. Directory Structure
Your folder should look like this:
```
project_root/
├── MainApplication.py
├── ... (other source files)
├── private_data/          <-- Not tracked by public Git
│   ├── __init__.py
│   ├── config.py          <-- Contains your secrets
│   ├── CustomerDatabase.xml
│   └── 2025-xx-xx_transaction_report.csv
```

## Usage
Run the main application:
```bash
python MainApplication.py
```
