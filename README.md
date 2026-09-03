# SmartStart OTA

Dette repository publicerer SmartStart-firmware som statiske HTTPS-filer via GitHub Pages.

## Offentlige adresser

- Manifest: `https://ota.greenier.dk/manifest.json`
- Firmware: adressen i manifestets `url`-felt

`image_sha256` er ESP-IDF-imagehashen, som firmwaren kontrollerer efter download. `file_sha256` kontrollerer hele den downloadede fil. De to værdier er med vilje forskellige.

## Udgivelsesforløb

1. Byg og test firmwaren på en fysisk enhed.
2. Læg `.bin`-filen i en ny versionsmappe under `firmware/`.
3. Opdater alle felter i `manifest.json`.
4. Push til `main`. Workflowet validerer fil, størrelse og hashes; GitHub Pages publicerer derefter indholdet.

Eksisterende versionsfiler må ikke overskrives. Opret altid en ny versionsmappe, så aktive enheder aldrig får en anden fil fra den samme URL.

## Sikkerhedsstatus

Denne første MVP-publicering bruger HTTPS og verificerer firmwarehashen. Manifestet er endnu ikke digitalt signeret (`signed_manifest: false`) og må derfor ikke bruges til uovervåget produktionsudrulning. Den kommende Base44/backend-integration skal signere manifestet, og ESP32'en skal kontrollere signaturen med en fast offentlig nøgle.

GitHub-repoet og Pages-siden indeholder ingen Wi-Fi-adgangskoder, private nøgler eller brugertokens.
