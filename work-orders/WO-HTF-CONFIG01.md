# WO-HTF-CONFIG01: HTF_CONFIG uhtlustamine + puuduvad instrumendid
P2 | src/engine/signal_filters.py | Gatekeeper: Risto

Branch: auto-claude/wo-htf-config01

## Taust

Audit (2026-03-17) avastas kaks probleemi HTF Trend filtris:

1. Asummeetria: MGC kasutas SMA(50) aga MNQ EMA(21) - 2.4x erinev reaktsioonikiirus.
   Tanane logi: MGC SMA(50) slope oli -7.80 ja -7.24 ajal mil MNQ EMA(21) naitas
   uptrendi - tulemus: 2 MGC SHORT tehingut laksid taide bullish turul (sig-3, sig-17).

2. Puuduvad instrumendid: NG, MCL ei ole HTF_CONFIG-s -> saavad vaikimisi MNQ
   seadistuse (EMA21) mis on energia instrumentide jaoks vale.

## Otsus MGC kohta (Risto, 2026-03-17)

MGC EMA periood: EMA(21), mitte EMA(34).
Pollhjus: kuld on praegu struktuuriliselt volatiilne (geopoliitika, Foed, tariifid,
keskpankade ostmine). See ei ole ajutine. MGC kaitumine on lahenemas MNQ-le.
Aeglasem HTF ei ole enam pohhjendatud — EMA(21) uhtsustab molemat instrumenti.

## Muutused - src/engine/signal_filters.py

### 1. HTF_CONFIG (read 138-145) - ASENDA kogu blokk

```python
HTF_CONFIG = {
    # Equity indices - EMA(21)
    "MNQ": {"ma_type": "ema", "ma_period": 21, "slope_bars": 3, "grace_bars": 4},
    "MES": {"ma_type": "ema", "ma_period": 21, "slope_bars": 3, "grace_bars": 4},
    "MYM": {"ma_type": "ema", "ma_period": 21, "slope_bars": 3, "grace_bars": 4},
    "M2K": {"ma_type": "ema", "ma_period": 21, "slope_bars": 3, "grace_bars": 4},
    # Metals - EMA(21): kuld on praegu sama volatiilne kui equity indeksid.
    # Otsus Risto 2026-03-17: ei pohhjenda enam aeglasemat HTF-i.
    "MGC": {"ma_type": "ema", "ma_period": 21, "slope_bars": 3, "grace_bars": 4},
    "MSI": {"ma_type": "ema", "ma_period": 21, "slope_bars": 3, "grace_bars": 4},
    # Energy - EMA(34): natgas vajab natuke sujuvamat HTF-i kui equity
    "NG":  {"ma_type": "ema", "ma_period": 34, "slope_bars": 4, "grace_bars": 5},
    "MCL": {"ma_type": "ema", "ma_period": 34, "slope_bars": 4, "grace_bars": 5},
}
```

### 2. TREND_STRATEGIES - ASENDA kogu blokk

```python
TREND_STRATEGIES = {
    "EMACrossover",
    "MACDMomentum",
    "BollingerBreakout",
    "FirstCandle",
    "FVGLiquiditySweep",
    "WallStreetPro",
    "NYOpenMomentum",         # momentum = trend
    "SessionHighLowBreakout", # breakout suunas = trend
    "LondonFakeout",          # momentum = trend
    "ATRExhaustion",          # trend exhaustion filter sobib
    "TopStepAPlus",           # trend-following
}
```

### 3. MEAN_REV_STRATEGIES - ASENDA kogu blokk

```python
MEAN_REV_STRATEGIES = {
    "RSIMeanReversion",
    "KelgusoiduStrategy",
    "GenjiDCA",
    "RSIReversalConfirmed",   # reversal = MR
    "VolumeSpikeReversal",    # reversal = MR
    "PreCloseUnwind",         # unwind = MR
    "BollingerMeanRevert",    # ilmselgelt MR
    "ConsecutiveFade",        # counter-trend = MR
}
```

### 4. BREAKOUT_STRATEGIES - ASENDA kogu blokk

```python
BREAKOUT_STRATEGIES = {
    "BollingerBreakout",
    "FVGLiquiditySweep",
    "NarrowRangeBreakout",    # breakout - korgem RVOL noue
    "OpeningRangeBreakout",   # breakout
    "EMARetest",              # breakout retest
}
```

## Testid - kirjuta tests/test_htf_config.py

1. test_mgc_uses_ema21 — MGC HTF_CONFIG["MGC"]["ma_type"] == "ema" ja period == 21
2. test_mnq_uses_ema21 — MNQ HTF_CONFIG["MNQ"]["ma_type"] == "ema" ja period == 21
3. test_ng_has_explicit_config — "NG" in HTF_CONFIG
4. test_mcl_has_explicit_config — "MCL" in HTF_CONFIG
5. test_all_active_strategies_classified:
   - Loe /home/brrr/brrr-printer2/data/strategy_library/*.json
   - Filtreeri kus active == True, kogu unikaalne strategy_name list
   - all_classified = TREND_STRATEGIES | MEAN_REV_STRATEGIES | BREAKOUT_STRATEGIES
   - Kontrolli et iga nimi on all_classified sees
   - Kui mitte -> assert False, f"Klassifitseerimata strateegia: {name}"
6. test_no_strategy_in_multiple_lists — iga strateegia max uhes listis

## Nouded

- Ainult signal_filters.py + uus tests/test_htf_config.py
- EI muuda filter_config.json
- EI muuda uhtegi teist parameetrit
- Engine restart pole vajalik

## Verification

```bash
cd /home/brrr/brrr-printer2
python -m pytest tests/test_htf_config.py -v
```

Eduka tulemusena peab MGC jargmine signaal logima:
  HTF Trend: HTF UP/DOWN (EMA(21) slope ...) - mitte enam SMA(50) ega EMA(34)
