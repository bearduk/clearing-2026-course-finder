# Clearing workbook input

Download the approved workbook from Teams/SharePoint into this directory using this exact filename:

`Clearing-2026-Course-Data-Master.xlsx`

Replace the previous local copy, then validate from the project root:

```bash
python3 build-clearing-data.py --dry-run inputs/Clearing-2026-Course-Data-Master.xlsx
```

After reviewing any warnings, create the upload package:

```bash
python3 build-clearing-data.py inputs/Clearing-2026-Course-Data-Master.xlsx
```

Outputs include `build/clearing-data/current/clearing-course-source-cms.html` for pasting into TerminalFour.

Excel workbooks in this directory are excluded from Git. Teams/SharePoint remains the master; this is only the downloaded build input.
