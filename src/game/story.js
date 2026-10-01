// The five acts. Objectives are tested against the save; progress is sticky (never undone).
// Objectives marked `soon` need systems that are not built yet: they are shown, but cannot be completed.
import { S, save } from './state.js';

const O = 'ORION';
export const ACTS = [
  {
    n: 1, title: 'Trezirea',
    intro: [
      { who: O, text: 'Odysseus… mă auzi? Sunt ORION. Ai dormit trei ani. Stația Orion-7 pierde energie de la impact.' },
      { who: O, text: 'Cristalele din hidroponică au început să strălucească. Cultivă-le: din ele facem combustibil.' },
      { who: O, text: 'Când energia scade, stația se întunecă. Ai o lanternă. Folosește-o.' },
    ],
    objectives: [
      { id: 'a1_harvest', text: 'Recoltează 3 resurse', done: (s) => s.counters.harvest >= 3, progress: (s) => `${Math.min(3, s.counters.harvest)}/3` },
      { id: 'a1_feed', text: 'Alimentează bio-generatorul', done: (s) => s.counters.feed >= 1 },
      { id: 'a1_flash', text: 'Pornește lanterna', done: (s) => !!s.flags.flashUsed },
      { id: 'a1_cmd', text: 'Intră în Centrul de comandă', done: (s) => !!s.flags.visitedCommand },
    ],
    outro: [{ who: O, text: 'Bine. Ai energie și ai hartă. Dar nu poți ține stația singur. E timpul să-i trezim pe ceilalți.' }],
  },
  {
    n: 2, title: 'Echipajul',
    intro: [
      { who: O, text: 'Reactorul e rece. Alimentează-l cu cristale, apoi folosește terminalul de criosomn din comandă.' },
      { who: O, text: 'Fiecare coleg trezit aduce ceva: Fermierul grăbește plantele, Inginerul încetinește pierderea de energie.' },
    ],
    objectives: [
      { id: 'a2_reactor', text: 'Alimentează reactorul (2 cristale)', done: (s) => s.counters.reactorFed >= 1 },
      { id: 'a2_farmer', text: 'Trezește Fermierul', done: (s) => s.crew.farmer },
      { id: 'a2_eng', text: 'Trezește Inginerul', done: (s) => s.crew.engineer },
      { id: 'a2_hangar', text: 'Verifică hangarul', done: (s) => !!s.flags.visitedHangar },
    ],
    outro: [{ who: O, text: 'Echipajul e treaz. Dar ceva s-a schimbat: cristalele pulsează un ritm. Un semnal.' }],
  },
  {
    n: 3, title: 'Semnalul',
    intro: [
      { who: O, text: 'Cristalele transmit un cod. Masa holografică îl poate decoda, dar are nevoie de un cristal rar.' },
      { who: O, text: 'Odată decodat, pregătim nava Meridian pentru prima expediție.' },
    ],
    objectives: [
      { id: 'a3_scan', text: 'Decodează semnalul (1 cristal rar)', done: (s) => !!s.flags.signalScanned },
      { id: 'a3_ship', text: 'Pregătește nava Meridian în hangar', done: (s) => !!s.flags.shipReady },
      { id: 'a3_go', text: 'Trimite prima expediție', soon: true },
    ],
    outro: [{ who: O, text: 'Meridian e pe rampă. Primul zbor începe.' }],
  },
  {
    n: 4, title: 'Amenințarea',
    intro: [{ who: O, text: 'Clanul Cenușei a detectat semnalul. Vor cristalele. Pregătește apărarea stației.' }],
    objectives: [{ id: 'a4_def', text: 'Apără stația de Clanul Cenușei', soon: true }],
    outro: [{ who: O, text: 'Au plecat. Pentru moment.' }],
  },
  {
    n: 5, title: 'Marea Recoltă',
    intro: [{ who: O, text: 'Semnalul e complet. Cultivatorii ne-au lăsat o alegere.' }],
    objectives: [{ id: 'a5_choice', text: 'Alege soarta ciclului Cultivatorilor', soon: true }],
    outro: [],
  },
];

export const currentAct = () => ACTS[S.act - 1];

export function objectivesView() {
  const a = currentAct();
  return { title: `Actul ${a.n} · ${a.title}`, list: a.objectives.map((o) => ({ text: o.text, done: !!S.objDone[o.id], soon: !!o.soon, progress: o.progress && !S.objDone[o.id] ? o.progress(S) : '' })) };
}

// Checks objectives, finishes the act when all are done, never goes backwards. Called ~2x per second.
export function updateStory(ui) {
  const a = currentAct();
  let changed = false;
  for (const o of a.objectives) {
    if (!S.objDone[o.id] && !o.soon && o.done(S)) { S.objDone[o.id] = true; changed = true; ui.toast('✓ ' + o.text); }
  }
  if (changed) { ui.setObjectives(objectivesView()); save(); }
  const allDone = a.objectives.every((o) => S.objDone[o.id]);
  const allImplemented = a.objectives.every((o) => o.soon || S.objDone[o.id]);
  const next = ACTS[S.act];
  if (allDone && next && !S.advancing) {
    S.advancing = true;
    ui.dialog(a.outro, () => {
      S.act += 1; S.advancing = false; save();
      ui.banner(`Actul ${next.n}`, next.title);
      ui.setObjectives(objectivesView());
      ui.dialog(next.intro);
    });
  } else if (allImplemented && !allDone && !S.flags['soon' + a.n]) {
    S.flags['soon' + a.n] = true; save();
    ui.dialog([{ who: O, text: `Asta e tot ce poți face din Actul ${a.n} în această versiune. Restul vine în actualizările următoare.` }]);
  }
}
