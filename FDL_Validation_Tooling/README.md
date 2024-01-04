# fdlchecker

`fdlchecker` is a Python script which validates FDL files. It uses the ASC FDL JSON Schema `ascfdl.schema.json` (see [JSON Schema](https://json-schema.org/)) which checks the structure and values against the ASC FDL Specification. Also it tests consistency of the ids used in the file, e.g. tests for duplicated IDs or IDs referenced but not defined, which cannot be acheived with a JSON Schema alone.

## How to use it

`fdlchecker` uses Python package `jsonschema` ([PyPI](https://pypi.org/project/jsonschema/)). It has been tested with `jsonschema` v4.20.0 (latest at time of writing).

```sh
# Recommend using a Python venv for this
python3 -m pip install jsonschema

python3 fdlchecker.py foo.fdl
```

## Example output

For instance here the `physical_dimensions` of one of our `canvases` has a negative `width`, which fails schema validation.

```sh
% python fdlchecker.py foo.fdl
===== Validating 'foo.fdl' =====
-1.0 is less than or equal to the minimum of 0

Failed validating 'exclusiveMinimum' in schema['properties']['contexts']['items']['properties']['canvases']['items']['properties']['physical_dimensions']['properties']['width']:
    {'exclusiveMinimum': 0, 'type': 'number'}

On instance['contexts'][0]['canvases'][0]['physical_dimensions']['width']:
    -1.0
```
