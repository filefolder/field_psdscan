# field_psdscan v0.1
A tool to quickly analyze power spectra of newly recorded seismic data for general on-site QC purposes

When servicing a seismic (etc) station it is nice to know it is still level and otherwise behaving properly before leaving so that the next service download isn't (also) ruined. "Tap Tests" are frequently misleading and shouldn't be relied on. This stupid (linux/osx/windows) script plots overlayed segments of probablistic PSDs relative to Peterson's (1993) background earth noise model using obspy's code (e.g. McNamara and Buland (2004)) for last four days of N-E-Z data. If the data is within the high/low noise models, that's good! If not, you should probably dig that sensor up.

Code is written with ANU (e.g. LPR-200 or TerraSAWR) seismic data loggers in mind but it is easily editable. Only requirement is Obspy & Python 3.8+ (probably lower will work as well). Any suggestions or comments fire away! xo RP
