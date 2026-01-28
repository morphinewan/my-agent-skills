# ASC CLI Command Reference

## Global Flags
- `--output <format>`: `json` (default), `table`, `markdown`.
- `--verbose`: Enable verbose logging.
- `--limit <n>`: Limit number of results.
- `--paginate`: Automatically fetch all pages.
- `--sort <field>`: Sort results (prefix with `-` for descending).

## Authentication (`asc auth`)
- `login`: Configure a new authentication profile.
- `logout`: Remove credentials.
- `status`: Check current auth status.
- `switch`: Switch between configured profiles.
- `list`: List all profiles.

## Apps (`asc apps`)
- `list`: List all apps.
- `search`: Search for apps.

## TestFlight (`asc testflight`, `asc beta-groups`, `asc beta-testers`)
- `beta-groups list/create/delete`: Manage beta groups.
- `beta-testers list/add/remove`: Manage testers.
- `builds list/expire`: Manage build availability.
- `feedback`: List beta feedback.
- `crashes`: List crash reports.

## App Store (`asc reviews`, `asc app-tags`)
- `reviews list`: Get customer reviews.
- `reviews respond`: Respond to a review.
- `app-tags list`: List tags associated with the app.

## Devices & Certificates (`asc devices`, `asc certificates`)
- `devices list`: List registered devices.
- `devices register`: Add a new device.
- `certificates list`: List signing certificates.
- `profiles list`: List provisioning profiles.

## Reports (`asc analytics`, `asc finance`)
- `analytics sales`: Download sales and trend reports.
- `finance reports`: Download financial reports.
