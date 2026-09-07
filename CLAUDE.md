# TERCET — pamięć projektu dla Claude (Code/Cowork)

Repo lampowego toru audio DIY. Pełny opis serii: `README.md`.
Każde urządzenie ma dokument ustaleń w `docs/PROJEKT-*.md` — **przeczytaj
dokument urządzenia, nad którym pracujesz, zanim cokolwiek zmienisz**.

## Konwencje repo
- Commity: po polsku, bez polskich znaków, prefiks obszaru
  (`headamp:`, `riaa:`, `docs:`); DECYZJE zapisujemy w docs/PROJEKT-*.md.
- Schematy RIAA są generowane skryptem (`riaa/gen.py` + `check.py` z
  asercjami netlisty). headamp na razie edytowany bezpośrednio przez
  Konnect/KiCad — plik `.kicad_sch` jest źródłem prawdy; generator TODO.
- `.gitignore` wycina PNG, svg_out/, PDF headampa i artefakty KiCada.
- Napięcia do ~330 V DC — zasady bezpieczeństwa w docs/ i na schematach.

## headamp — stan na 2026-09-07
- Wzmacniacz słuchawkowy SE: ½ ECC82 → EL84 (trioda, zwora R9 100R) →
  OPT 5k:80 (DT 770 M). Zero półprzewodników w torze; NFB brak (decyzja).
- `headamp/headamp.kicad_sch`: **kanał L kompletny, ERC 0 błędów**.
  Ostrzeżenia oczekiwane: wolny unit B ECC82 (kanał P), wiszące IN_L/OUT_L.
- Numeracja na schemacie (≠ wcześniejsze dokumenty): C2=1µ katoda stała,
  C3=100µ za SW2 ("wokal do przodu"), C5=100n sprzęgający, C6=470µ katoda
  EL84, R9=zwora triodowa. Schemat = źródło prawdy.
- Symulacje ngspice w `headamp/sim/` (modele Korena): gain 24,7 dB,
  THD 0,2% @0,6Vrms (dominacja H2), Zout ~36 Ω, dół -3 dB @24 Hz przy
  Lp=15 H → OPT zamawiać z Lp ≥ 25 H.
- Crossfeed S1 (pasywny, DPDT) zaprojektowany i zasymulowany —
  `headamp/sim/crossfeed.cir`, jeszcze NIE narysowany w KiCadzie.
- Pełna pamięć projektu: `docs/PROJEKT-HEADAMP.md` (wymagania, decyzje,
  wartości, wyniki symulacji, TODO).

## Następne kroki headamp (kolejność sugerowana)
1. Kanał P: unit B ECC82 (U1, pins 1/2/3) + drugi EL84 + drugi OPT.
2. Arkusz zasilacza: B+ (CLC) + żarzenie DC z `common/` (LD1085,
   elewacja +50 V) + rozładowanie B+.
3. Crossfeed S1 + gniazda WE/WY na schemacie.
4. `headamp/check.py` z asercjami netlisty (wzór: `riaa/check.py`).
5. BOM (TME) + specyfikacja OPT dla nawijacza.

## Narzędzia
- KiCad 10.0.6 (instalacja per-user:
  `C:\Users\wikto\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe`).
- MCP **Konnect** (wtyczka PCM; binarka i `settings.json` w
  `...\Documents\KiCad\10.0\3rdparty\plugins\com_github_mixelpixx_konnect\bin\`).
  Ustawione: `eager_toolsets=true` (Claude Desktop nie odświeża listy
  narzędzi po load_toolset), `kicad_cli=<ścieżka wyżej>`.
  Narzędzia PCB wymagają ręcznej konfiguracji IPC (KiCad: Preferences →
  Plugins → Enable KiCad API; adres wkleić w Tools → External Plugins →
  Konnect) — jeszcze NIE zrobione; do schematów niepotrzebne.
- Symulacje: ngspice (`ngspice -b headamp/sim/amp.cir`).
- Git w VM Cowork zostawia martwe `.lock`/`tmp_obj_*` w `.git`
  (brak uprawnień unlink) — po commitach sprzątać, inaczej blokują gita.
