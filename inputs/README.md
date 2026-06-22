# Clearing workbook input

Download the approved workbook from Teams/SharePoint into this directory using this exact filename:

`Clearing-2026-Course-Data-Master.xlsx`

Replace the previous local copy, then validate it from the project root:

```bash
python3 build-clearing-data.py --dry-run
```

After reviewing any warnings, create the upload package with:

```bash
python3 build-clearing-data.py
```

Excel workbooks in this directory are excluded from Git and GitHub Pages. Teams/SharePoint remains the master and version history; this is only the downloaded build input.
