---
name: asc-cli
description: Automate App Store Connect tasks using the `asc` CLI tool. Supports TestFlight management, app metadata, localizations, certificates, devices, analytics, and sales reports. Use when automating release workflows or querying App Store Connect data.
---

# App Store Connect CLI (asc)

## Overview

This skill provides comprehensive instructions for using the `asc` command-line tool to interact with App Store Connect. It covers authentication, managing TestFlight (beta testers, groups, builds), app metadata, devices, and generating reports. The tool outputs JSON by default, making it ideal for automation.

## Authentication

Before running commands, ensure you are authenticated.

### Setup
1.  **API Key**: You need an API Key from App Store Connect (Keys section).
2.  **Login**:
    ```bash
    asc auth login \
      --name "MyProfile" \
      --key-id "YOUR_KEY_ID" \
      --issuer-id "YOUR_ISSUER_ID" \
      --private-key /path/to/AuthKey.p8
    ```
3.  **Check Status**: `asc auth status`

### Environment Variables
For convenience, you can set the following environment variables in your shell profile (e.g., `.zshrc` or `.bashrc`):
- `ASC_VENDOR_NUMBER`: Set this to your 8-digit Vendor ID (e.g., `YOUR_VENDOR_ID`) to avoid providing `--vendor` in every report command.

## Core Capabilities

### 1. TestFlight Management

**Beta Groups & Testers:**
- List groups: `asc beta-groups list --app "APP_ID"`
- Create group: `asc beta-groups create --app "APP_ID" --name "Group Name"`
- List testers: `asc beta-testers list --app "APP_ID"`
- Add tester: `asc beta-testers add --app "APP_ID" --email "email@example.com" --group "Group Name"`

**Builds:**
- List builds: `asc builds list --app "APP_ID"`
- Expire build: `asc builds expire --build "BUILD_ID"`
- Distribute: `asc builds distribute --app "APP_ID" --build "BUILD_ID" --group "Group Name"`

### 2. App Metadata & Configuration

- **List Apps**: `asc apps` (outputs list of all apps)
- **App Info**: `asc app-setup info set --app "APP_ID" --primary-locale "en-US"`
- **Categories**: `asc app-setup categories set --app "APP_ID" --primary GAMES`
- **Pricing**: `asc pricing available` (check tiers)

### 3. Devices & Profiles

- **List Devices**: `asc devices list`
- **Register Device**: `asc devices register --name "Device Name" --udid "UDID" --platform IOS`
- **Certificates**: `asc certificates list`

### 4. Analytics & Reports

**Vendor ID**: Required for most reports. If unknown, check the App Store Connect website or previous report filenames. The CLI does not currently have a command to list Vendor IDs directly.

**Daily Sales Report**:
-   **Note on Latency**: Daily reports are **not real-time**. They are typically available for the *previous day* (T-1) or two days ago (T-2), depending on the timezone (usually after 5 AM PST).
-   **Command**:
    ```bash
    asc analytics sales \
      --vendor "YOUR_VENDOR_ID" \
      --type SALES \
      --subtype SUMMARY \
      --frequency DAILY \
      --date "YYYY-MM-DD" \
      --decompress
    ```
-   **Output**: A TSV (Tab-Separated Values) file.
-   **Viewing**: Use `head` or `column -t` to view the decompressed TSV file.
    ```bash
    head -n 20 sales_report_YYYY-MM-DD_SALES.tsv
    ```

**Finance Reports**:
-   **Monthly Financials**:
    ```bash
    asc finance reports --vendor "YOUR_VENDOR_ID" --report-type FINANCIAL --region "ZZ" --date "YYYY-MM"
    ```

### 5. Submission & Review

- **Submit for Review**:
    ```bash
    asc submit create --app "APP_ID" --version "1.0.0" --build "BUILD_ID" --confirm
    ```

## Advanced Usage

### JSON Processing
All commands output minified JSON by default. Use `jq` to parse:
  ```bash
# Get the App ID of the first app
asc apps | jq -r '.[0].id'
  ```

### Real-Time Data Limitations
The `asc` CLI interacts with the App Store Connect API, which provides **reporting data** (Sales, Finance) and **configuration data** (Apps, Builds). It does **not** provide real-time transaction streams or active subscription counters. For real-time events, rely on App Store Server Notifications sent to your backend.

### Reference
For a complete list of commands and detailed usage, see [COMMANDS.md](references/commands.md).