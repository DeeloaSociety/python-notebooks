## How its work

Opening lakasir_dlt.ipynb for **data exploration and fetching with [dltHub](https://github.com/dlt-hub/dlt)**,

**Set up** your environment first,

```python
lakasirClient = LakasirClient(
    base_url=os.getenv("LAKASIR_BASE_URL"),
    email=os.getenv("LAKASIR_EMAIL"),
    password=os.getenv("LAKASIR_PASSWORD")
)
```

**Update the pipeline** if necessary,
```python
pipeline = dlt.pipeline(
    pipeline_name="lakasir",
    destination="duckdb",
    
    # refresh is 'replace' for effectively performing a full data replacement on each update.
    # refresh="replace",
)
```

**Update pages** for initial page or last page on fetching data,
```python
def sell_details():
    page = 1
    per_page = 10
    has_more_pages = True
```

**Update dates** (start date and end date) on fetching data,
```python
START_DATE = "2025-09-01"
END_DATE = "2025-09-11"
```

**Editable and reactive the notebook** with cell or interact with a UI
element, please fetching data through lakasir_dlt.ipynb first before doing this.
```bash
marimo edit lakasir_dashboard.py
```

Run **the notebook as a web app**,
```bash
marimo run lakasir_dashboard.py
```