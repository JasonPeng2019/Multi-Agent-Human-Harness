# Pinned Zstd benchmark image

`zstd-decoder-asset-repair-v2-20261015.docker.tar` is a Docker **image** archive,
including its layers. It is the corrected benchmark image used by both the
public-check bridge and operator grading:

```
swe-marathon-zstd-decoder:asset-repair-v2-20261015
sha256:cfe037596ca5fd52d050f98a75ba5b9b74fa45d909ea55002c57bab7157659fb
```

`ZSTD_IMAGE_EXPORT.json` records the archive's SHA-256, size, exact image ID,
and whether export and config verification completed. Verify its status is
`EXPORTED_AND_VERIFIED` and compare the archive hash before transferring/loading.

On this machine the pinned image is already installed. On another Docker host:

```powershell
Get-FileHash .\images\zstd-decoder-asset-repair-v2-20261015.docker.tar -Algorithm SHA256
docker image load --input .\images\zstd-decoder-asset-repair-v2-20261015.docker.tar
docker image inspect swe-marathon-zstd-decoder:asset-repair-v2-20261015 --format '{{.Id}}'
```

Run from the bundle root and compare both outputs against the receipt and image
ID above. Loading an image does not launch a benchmark. A rebuild normally has a
different image ID and must not silently replace the pin; it requires asset-byte
verification, unchanged oracle calibration of 43/43, and deliberate configuration
updates. The historical `lf-20260925` image has corrupt expected-output bytes and
must not be used for new scores.

The export contains sealed operator evaluation assets. Keep it and the upstream
hidden tests/reference solutions outside live task workspaces and memory.
