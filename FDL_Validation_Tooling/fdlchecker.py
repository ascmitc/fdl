#! /usr/bin/env python3

import argparse
import json
import pathlib
import sys

import jsonschema

SCHEMA_PATH=pathlib.Path(__file__).absolute().parent / 'ascfdl.schema.json'

def validate_id_tree(fdl):
    fi_ids = set()

    for fi in fdl.get("framing_intents", []):
        fi_id = fi["id"]
        fi_label = fi["label"]
        if fi_id in fi_ids:
            raise RuntimeError(f"Framing Intent {fi_id} ({fi_label}): ID duplicated")
        fi_ids.add(fi_id)

    if "default_framing_intent" in fdl:
        default_framing_intent = fdl["default_framing_intent"]
        if not default_framing_intent in fi_ids:
            raise RuntimeError(f"Default Framing Intent {default_framing_intent}: Not in framing_intents")

    cv_ids = set()
    cv_source_canvas_ids = set()
    fd_ids = set()

    for cx in fdl.get("contexts", []):
        cx_label = cx["label"]

        for cv in cx.get("canvases", []):
            cv_id = cv["id"]
            cv_label = cv["label"]

            cv_source_canvas_id = cv["source_canvas_id"]
            cv_source_canvas_ids.add(cv_source_canvas_id)

            if cv_id in cv_ids:
                raise RuntimeError(f"Context ({cx_label}) > Canvas {cv_id} ({cv_label}): ID duplicated")
            cv_ids.add(cv_id)

            for fd in cv.get("framing_decisions", []):
                fd_id = fd["id"]

                if fd_id in fd_ids:
                    raise RuntimeError(f"Context ({cx_label}) > Canvas {cv_id} ({cv_label}) > Framing Decision {fd_id}: ID duplicated")
                fd_ids.add(fd_id)

                fd_framing_intent_id = fd["framing_intent_id"]

                if fd_framing_intent_id not in fi_ids:
                    raise RuntimeError(f"Context ({cx_label}) > Canvas {cv_id} ({cv_label}) > Framing Decision {fd_id}: Framing Intent ID {fd_framing_intent_id} not in framing_intents")

                expected_fd_id = f"{cv_id}-{fd_framing_intent_id}"
                if fd_id != expected_fd_id:
                    raise RuntimeError(f"Context ({cx_label}) > Canvas {cv_id} ({cv_label}) > Framing Decision {fd_id}: ID doesn't match expected {expected_fd_id}")

    unrecognised_cv_ids = cv_source_canvas_ids - cv_ids
    if len(unrecognised_cv_ids) > 0:
        raise RuntimeError(f"Source Canvas IDs {list(unrecognised_cv_ids)} not in canvases")

    ct_ids = set()
    for ct in fdl.get("canvas_templates", []):
        ct_id = ct["id"]
        ct_label = ct["label"]

        if ct_id in ct_ids:
            raise RuntimeError(f"Canvas Template {ct_id} ({ct_label}): ID duplicated")
        ct_ids.add(ct_id)


def validate_fdl(filename):
    print(f"===== Validating '{filename}' =====")
    errors = 0
    schema = None
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)

    with open(filename) as f:
        try:
            fdl = json.load(f)
        except json.decoder.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            errors += 1
            return errors

        Validator = jsonschema.validators.validator_for(schema)
        v = Validator(schema=schema, format_checker=Validator.FORMAT_CHECKER)
        for error in v.iter_errors(fdl):
            print(str(error))
            errors += 1

        try:
            validate_id_tree(fdl)
        except RuntimeError as e:
            print(f"ID Tree Error: {e}")
            errors += 1
            return errors

    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = 'ascfdl_schema_test',
        description = 'validate FDL files using JSON Schema'
    )
    parser.add_argument('fdl_file', type=pathlib.Path, nargs='*')
    args = parser.parse_args()

    errors = 0

    for fdl_file in args.fdl_file:
        errors += validate_fdl(fdl_file)

    sys.exit(errors)
