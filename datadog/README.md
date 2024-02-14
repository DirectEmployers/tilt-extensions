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
argument to `datadog_up`.

```starlark
datadog_up(agent_image_tag = "7.50.3")
```
> **Note**: If multiple Tilt sessions are started, the Datadog extension will only be able to respect the arguments 
> of a single session (likely the first place the Datadog extension is invoked). This could result in surprising and 
> unexpected results, but would only occur in the rare circumstance that multiple Tilt sessions would be required in 
> the first place.
