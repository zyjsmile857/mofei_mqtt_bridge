# Repository Setup

This repository is prepared for the GitHub user or organization `zyjsmile857`.

Recommended GitHub repository:

```text
zyjsmile857/mofei_mqtt_bridge
```

## GitHub Settings

- Make the repository public.
- Add a repository description.
- Enable Issues.
- Add topics: `home-assistant`, `hacs`, `mqtt`, `custom-component`, `integration`.
- Push this repository as the root of the GitHub repository.

## Checks

Both workflows must pass:

- `Validate`
- `Validate with hassfest`

## Release

After the workflows pass, create a full GitHub release, not only a tag.

Suggested first release:

```text
v0.1.0
```

## HACS Default PR

Fork `hacs/default`, edit the `integration` file, and add:

```json
"zyjsmile857/mofei_mqtt_bridge"
```

Keep the list alphabetically sorted, then open a pull request to `hacs/default`.
