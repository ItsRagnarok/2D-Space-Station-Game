# Planul de bătaie

## Ce există acum
- Joc web (Phaser + Vite) pus pe Vercel; același cod va merge în Capacitor (Android/iOS) și Electron (Steam).
- Cameră de hidroponică jucabilă: Odysseus în 4 direcții (mers animat, costum de stație + costum EVA generat), coliziuni, umbre, cultivare în 3 stadii, bio-generator, regula energiei (întuneric, lanternă, lămpi de urgență).
- Controale: tastatură (WASD), mouse (click stânga acțiune, click dreapta lanternă), joystick și butoane pe telefon. PWA pentru ecran complet pe iPhone.
- Forja de asset-uri (`tools/assets/forge/`): un master per asset, variante derivate din cod (oglindire, recolorare, scalare), atlas pentru joc.

## Starea actelor (în joc acum)
Progresul se salvează local și **merge doar înainte**. Singura cale înapoi e *Meniu → Reset total* (cu confirmare), care șterge tot și reîncepe de la Actul 1.

| Act | Ce se poate juca acum | Ce lipsește |
|---|---|---|
| 1 Trezirea | complet: recoltare, bio-generator, lanternă, intrare în comandă | nimic |
| 2 Echipajul | complet: alimentat reactorul, trezit Fermierul și Inginerul (bonusuri reale), vizitat hangarul | nimic |
| 3 Semnalul | decodat semnalul (masa holografică), pregătită nava Meridian | „Trimite prima expediție" (E6) |
| 4 Amenințarea | doar introducerea | luptă și apărarea stației (E7) |
| 5 Marea Recoltă | doar introducerea | alegerea finală (E9) |

## Seturile de asset-uri (în ordinea construirii)
| # | Set | Conține | Stare |
|---|---|---|---|
| S1 | Personaje | Odysseus ✓, costum EVA ✓ (de integrat), 5 membri de echipaj (recolorări + trăsături), portrete pentru dialog, poze: cară, repară, rănit | parțial |
| S2 | Camere de stație | hidroponică ✓, **reactor ✓, hangar ✓, comandă ✓** (uși, terminal ORION, terminal criosomn, masă holografică, navă, fereastră spre spațiu), laborator (scena există, de integrat), depozit, infirmerie, atelier | parțial |
| S3 | Stația din spațiu | **module văzute de sus ✓** (hidroponică, comandă, reactor, hangar, laborator în construcție), panouri solare ✓, antene ✓, propulsoare animate ✓, conectori ✓, planetă sterpă ✓, stele ✓; lipsesc: docuri cu nave care sosesc, piese pentru extindere | parțial |
| S4 | Nave | nava jucătorului (16 unghiuri din Blender), cargo, scout, miner, 3 nave pirat, sateliți abandonați; variante în hangar (3/4) | de făcut |
| S5 | Spațiu și lumi | asteroizi, 3 planete (peșteri cu cristale, junglă toxică, gheață), teren de explorare, interior de stație abandonată | de făcut |
| S6 | Viață și resurse | mai multe plante/cristale, 4 creaturi noi (meduza ✓), obiecte de recoltat, artefacte | parțial |
| S7 | Interfață | panouri, iconițe, dialog cu portrete, hartă, inventar, setări | parțial (HUD DOM) |
| S8 | Efecte și lumină | scântei, aburi, holograme, propulsoare, explozii, raze; lanternă ✓, lămpi de urgență ✓ | parțial |
| S9 | Sunet | muzică ambientală, pași, uși, recoltă, alarmă, voce ORION | de făcut |

## Vedere și navigare
- **Zoom:** rotiță de mouse, ciupire pe telefon, butoanele − / + sau tastele − / +. Când te îndepărtezi, camera plutește în spațiu, cu stele și planeta în fundal.
- **Harta stației (M sau butonul Hartă):** toată stația văzută din spațiu, în mișcare; alegi un modul și te teleportezi acolo. Laboratorul e blocat până la Actul 3.
- **De făcut:** controlul personajului în exterior (spacewalk cu costumul EVA) și docurile cu nave.

## Etapele jocului (cod)
1. **E1 Felia de bază** ✓ (cameră, personaj, cultivare, energie).
2. **E2 Stația ca hartă** ✓ (4 camere legate prin uși, reactor ca sursă de energie); lipsește minihărta.
3. **E3 Salvare și conturi:** progres salvat local, apoi cont (Supabase) pentru telefon/PC.
4. **E4 Echipajul:** criosomn, trezirea colegilor, roluri care deblochează camere.
5. **E5 Hangar și nave:** nave care sosesc și pleacă, marfă, reparații.
6. **E6 Misiuni și explorare:** harta spațiului, planete/asteroizi/sateliți, recompense.
7. **E7 Evenimente și luptă:** furtuni, semnalul, *Apără stația*.
8. **E8 Cercetare și dezvoltare:** arbore de upgrade-uri, extinderea stației.
9. **E9 Poveste:** dialoguri, acte, final.
10. **E10 Lansare:** Android (Capacitor), iOS, Steam (Electron + Steamworks).

## Ordinea de lucru pe fiecare etapă
asset-uri (master → variante) → verificare vizuală pe o foaie → integrare în joc → test live → deploy. Fiecare etapă într-o sesiune nouă, cu aceste documente ca predare.

## Decizii deschise
Numele stației și ale personajelor; dacă povestea are 2 finaluri; cine face arta „bogată"; ritmul de scădere a energiei (după teste).
