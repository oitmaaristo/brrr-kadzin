# WO-SLTP: SL/TP ATR Multiplierid - Uks Allikas, Uks Tode
**P2** | brrr-printer2 src/engine/ | Gatekeeper: Risto

## Probleem
SL/TP multiplierid defineeritud mitmes kohas, ebaselge kumb voidab:
- strategy_library JSON: atr_sl_mult=0.5, atr_tp_mult=2.33 (per strateegia)
- BracketConfig default: sl_atr_mult=0.75, tp_atr_mult=3.0 (bracket_executor.py:99)
- signal_generator.py _get_sl_mult() fallback: return 0.75

## Fix 1: Kaardista koik kohad
grep -rn atr_sl_mult kogu brrr-printer2 repo. Loenda koik kohad.

## Fix 2: Defineeri hierarhia
1. strategy_library JSON settings (korgeim prioriteet)
2. Strateegia klassi DEFAULT_PARAMS
3. BracketConfig default (madalaim prioriteet)

## Fix 3: Logi iga trade alguses
Using SL=Xx TP=Yx from [json|class|default]

## Fix 4: Puhastumine
Eemalda duplikaadid, uks allikas, uks tode.

## Testimine
bollingerbreakout-mgc-15m-v1 peab kasutama JSON 0.5/2.33, mitte 0.75/3.0.
