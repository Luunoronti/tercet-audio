# common — bloki współdzielone serii TERCET

Bloki projektowane z myślą o reużyciu we wszystkich trzech urządzeniach
(na razie opisane w schemacie RIAA; przy końcówce mocy wydzielimy je tu
jako wspólne moduły/PCB):

- **Żarzenie DC**: uzwojenie ~7 V → mostek Schottky (1N5822) → 10000 µF →
  LDO LD1085 → 6,3 V DC, z elewacją do +50 V (dzielnik z B+).
- **Automatyka**: K1 — rozładowanie kondensatorów po zaniku sieci
  (styk NC + rezystor mocy); K2/K3 — wyciszanie wyjść z opóźnieniem
  (2N7000 + RC), natychmiastowy mute przy wyłączeniu.
- **Ground breaker**: 10R/5W ∥ 2× 1N5408 antyrównolegle ∥ 100n —
  jedyny punkt styku masy sygnałowej z chassis/PE.
- **Wejście sieciowe**: IEC + bezpiecznik → wyłącznik DPST → NTC →
  transformator; warystor; neonówka jako kontrolka.
