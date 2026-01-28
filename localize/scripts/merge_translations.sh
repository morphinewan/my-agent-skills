#!/bin/bash

# check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <xcstrings_path> <translations_json_path>"
    exit 1
fi

XCSTRINGS_PATH=$1
TRANSLATIONS_PATH=$2

# check if files exist
if [ ! -f "$XCSTRINGS_PATH" ]; then
    echo "Error: .xcstrings file not found at $XCSTRINGS_PATH"
    exit 1
fi

if [ ! -f "$TRANSLATIONS_PATH" ]; then
    echo "Error: Translations JSON file not found at $TRANSLATIONS_PATH"
    exit 1
fi

echo "Starting merge using jq..."
echo "Source: $TRANSLATIONS_PATH"
echo "Target: $XCSTRINGS_PATH"

# Use jq to merge. 
# -s reads input into an array
# .[0] is the xcstrings file (first argument to jq), .[1] is the translations (second argument)
# * operator does a deep merge
# We output to a temp file first
TMP_FILE="${XCSTRINGS_PATH}.tmp"

jq -s '.[0] * .[1]' "$XCSTRINGS_PATH" "$TRANSLATIONS_PATH" > "$TMP_FILE"

if [ $? -eq 0 ]; then
    mv "$TMP_FILE" "$XCSTRINGS_PATH"
    echo "Success! Merged translations into $XCSTRINGS_PATH"
else
    echo "Error: jq merge failed."
    rm -f "$TMP_FILE"
    exit 1
fi
