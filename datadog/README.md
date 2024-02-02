# Datadog

Add a button to the Tilt UI to toggle Datadog agent resources using Helm.

## Usage

After registering the repo and extension (see [main README](../README.md)), you can invoke the extension using
`datadog_up` in your Tiltfile. This will add a button to the global Tilt UI (a paw print icon) which can toggle
Datadog resources on and off. Datadog API and App keys are required and can be added through the button's dropdown menu.

```starlark
load("ext://datadog", "datadog_up")

datadog_up()  # This does not accept any arguments at this time.
```
