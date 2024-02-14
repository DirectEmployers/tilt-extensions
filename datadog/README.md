# Datadog

Add a button to the Tilt UI to toggle Datadog agent resources using Helm.

## Requirements

- Tilt >= 0.33.5
- Python >= 3.11

## Usage

After registering the repo and extension (see [main README](../README.md)), you can invoke the extension using
`datadog_up` in your Tiltfile. This will add a button to the global Tilt UI (a paw print icon) which can toggle
Datadog resources on and off. Datadog API and App keys are required and can be added through the button's dropdown menu.

```starlark
load("ext://datadog", "datadog_up")

datadog_up()
```

If you need to lock a project  to a specific Datadog Agent image tag/version, you can provide a valid image tag as an 
argument to `datadog_up`:

```starlark
datadog_up(agent_image_tag = "7.50.3")
```
