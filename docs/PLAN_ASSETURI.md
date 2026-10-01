# Plan de asset-uri (economic)

## Stil fix (nu se mai schimbă, ca să nu refacem)
- Perspectivă 3/4 ortogonală, grilă 16×16 px, scenă 320×180 mărită ×3 (landscape).
- Paletă: oțel (9 trepte), portocaliu (6), teal (5), albastru holo (6), verde (4), roșu urgență (3). Contur întunecat `#101216`.
- Lumina vine din stânga-sus. Umbre dure sub obiecte. Lumina dinamică (întuneric, lanternă, lămpi) se face **în cod**, nu în sprite-uri.

## Faze
**Faza 0 — făcută:** forja de cod (`tools/assets/forge/`), 55 de sprite-uri pentru camera de cercetare, 5 iconițe HUD, scena cu HUD și animația, regula de întuneric.

**Faza 1 — felia jucabilă (prioritară):**
- plăci de podea/pereți cu colțuri, uși (4 cadre), tranziții între camere;
- astronaut cu **mers în 3 direcții** (jos, sus, lateral; stânga = oglindit) × 4 cadre, plus stat, lucru, cărat celulă;
- reactor animat (4 cadre), celulă de energie, lanternă (con în cod), lampă de urgență (2 cadre), stație de încărcare;
- cultivare: paturi + 3 stadii de creștere × 4 culturi;
- hangar: platformă + navă (stat, propulsoare 3 cadre);
- iconițe de resurse și bare de HUD.

**Faza 2 — spațiul:** navă văzută de sus în 16 unghiuri (randare Blender → pixel art, nu rotire de pixeli), 6 asteroizi, planetă, inamici, efecte (rază, explozii).

**Faza 3 — finisaj:** particule, aburi, scântei, skin de interfață, sunete.

## Cum reducem consumul (credite)
1. **Generăm în serie, verificăm o singură imagine** (foaie cu toate sprite-urile dintr-un lot), nu câte una.
2. **Variante prin recolorare și oglindire**, nu desen nou (3 culori de astronaut din același șablon; stânga = dreapta oglindit).
3. **Verificări automate** (dimensiune pe grilă, paletă, margini transparente) în loc de revizuire vizuală.
4. **Lumina în cod**: întuneric, lanternă și lămpi nu cer sprite-uri noi.
5. **Doar codul în git**; PNG-urile generate se refac oricând (`tools/assets/out/` ignorat).
6. **Sesiuni scurte pe faze**: conversația lungă se recitește la fiecare mesaj și costă. Începem fiecare fază într-o sesiune nouă, cu acest document ca predare.
7. **Piesele complexe** (artă bogată, ilustrații) le poate face un artist sau un generator; noi facem partea de cod și integrare.

## Decizii deschise
- Ritmul de scădere a energiei și costul celulelor (se stabilesc la test).
- Dacă personajul are mers în 4 sau 8 direcții.
- Cine face arta „bogată" (noi, tu, un artist).
