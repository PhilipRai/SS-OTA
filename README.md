# SmartStart OTA

Dette repository publicerer SmartStart-firmware som statiske HTTPS-filer via GitHub Pages.

## Offentlige adresser

- Manifest: `https://ota.greenier.dk/manifest.json`
- Firmware: adressen i manifestets `url`-felt

`image_sha256` er ESP-IDF-imagehashen, som firmwaren kontrollerer efter download. `file_sha256` kontrollerer hele den downloadede fil. De to værdier er med vilje forskellige. Manifestet signeres med ECDSA P-256; kun den offentlige nøgle ligger i GitHub.

## Udgivelsesforløb

1. Byg og test firmwaren på en fysisk enhed.
2. Læg `.bin`-filen i en ny versionsmappe under `firmware/`.
3. Opdater alle felter i `manifest.json`, herunder det monotont stigende `sequence`.
4. Signér manifestet lokalt: `python3 tools/sign_manifest.py ~/.smartstart-keys/ota-signing-private.pem`.
5. Kør `python3 tools/verify_release.py`.
6. Push til `main`. Workflowet validerer fil, størrelse, hashes og signatur; GitHub Pages publicerer derefter indholdet.

Eksisterende versionsfiler må ikke overskrives. Opret altid en ny versionsmappe, så aktive enheder aldrig får en anden fil fra den samme URL.

## Sikkerhedsstatus

OTA-klienten kræver både HTTPS, stigende sekvensnummer, korrekt firmwarehash og en gyldig ECDSA-signatur. Den private nøgle må aldrig kopieres til GitHub, firmware eller en ESP32. Senere kan signeringen flyttes til en isoleret release-tjeneste eller KMS.

GitHub-repoet og Pages-siden indeholder ingen Wi-Fi-adgangskoder, private nøgler eller brugertokens.
