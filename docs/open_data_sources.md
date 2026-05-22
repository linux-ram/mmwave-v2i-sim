# Open Data and Asset Provenance

Bundled assets are from the MIT-licensed MATLAB reference repository
[linux-ram/mmWave-V2I-2DRBP](https://github.com/linux-ram/mmWave-V2I-2DRBP).

## Bundled Files

| File | Source | License | Notes |
|------|--------|---------|-------|
| `assets/CitySectionAerialView.png` | mmWave-V2I-2DRBP | MIT | Aerial map background for Figure 1 |
| `assets/vehicularRoutes.mat` | mmWave-V2I-2DRBP | MIT | Original 10 base vehicular routes + BS position |
| `assets/vehicular_routes.npz` | Converted from `.mat` | MIT | Open redistribution format (`scripts/convert_matlab_assets.py`) |
| `assets/base_station.json` | Converted from `.mat` | MIT | Base station coordinates |
| `vendor/RectangleBinPack/` | [juj/RectangleBinPack](https://github.com/juj/RectangleBinPack) | Public Domain | Guillotine 2DRBP packing parity binary |

## Conversion

Run once after updating the MATLAB `.mat` source:

```bash
python scripts/convert_matlab_assets.py
```

## Planned Future Source Classes

- OpenStreetMap roadway topology (ODbL)
- Public building footprint datasets where available
- Open 3D city models with permissive redistribution licenses

## License Gate

Before bundling any additional city mesh/texture dataset:

1. Record source URL
2. Record exact license
3. Confirm redistribution rights
4. Store attribution text
5. Add dataset checksum and version date
