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
- **Schemat generowany skryptem `headamp/gen.py`** (jak `riaa/gen.py`) —
  **NIE edytować `headamp.kicad_sch` ręcznie w Eeschema/Konnect**, zmiany
  wprowadzać w `gen.py` i regenerować. Workflow (3 komendy) i szczegóły:
  `headamp/README.md`.
- `headamp/headamp.kicad_sch`: **kanał L + kanał P + zasilacz kompletne,
  ERC 0 błędów**. Ostrzeżenia oczekiwane: wiszące IN_L/IN_R/OUT_L/OUT_R
  (do czasu gniazd/crossfeedu), multiple_net_names ELEV/HEAT_B (zamierzone,
  jak w common/riaa). Paper A2 (zmienione z A3 w Etapie 5b - nie mieściło
  się z zasilaczem).
- Numeracja na schemacie (≠ wcześniejsze dokumenty): C2=1µ katoda stała,
  C3=100µ za SW2 ("wokal do przodu"), C5=100n sprzęgający, C6=470µ katoda
  EL84, R9=zwora triodowa (kanał L); kanał P = refy +200 (R201.., C201..,
  SW202, T201, U202); zasilacz = refy 3xx + wyjątki nazwane wprost (F1,
  SW1, J1, RT1, RV301, NE1, T301, L1, K1, U301). Schemat = źródło prawdy.
- RV1 = potencjometr podwójny (`Device:R_Potentiometer_Dual_Separate`,
  unit1=L/unit2=P) - DECYZJA, patrz docs/PROJEKT-HEADAMP.md.
- Symulacje ngspice w `headamp/sim/` (modele Korena): gain 24,7 dB,
  THD 0,2% @0,6Vrms (dominacja H2), Zout ~36 Ω, dół -3 dB @24 Hz przy
  Lp=15 H → OPT zamawiać z Lp ≥ 25 H.
- Crossfeed S1 (pasywny, DPDT) zaprojektowany i zasymulowany —
  `headamp/sim/crossfeed.cir`, jeszcze NIE narysowany w KiCadzie.
- Pełna pamięć projektu: `docs/PROJEKT-HEADAMP.md` (wymagania, decyzje,
  wartości, wyniki symulacji, TODO).

## Następne kroki headamp (kolejność sugerowana)
1. Crossfeed S1 + gniazda WE/WY na schemacie.
2. Estetyka schematu (nakładające się pola, czytelność zasilacza).
3. BOM (TME) + specyfikacja OPT dla nawijacza.

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
