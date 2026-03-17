# WO-HTF-CONFIG01: HTF_CONFIG uhtlustamine + puuduvad instrumendid
P2 | src/engine/signal_filters.py | Gatekeeper: Risto

Branch: auto-claude/wo-htf-config01

## Taust

Audit (2026-03-17) avastas kaks probleemi HTF Trend filtris:

1. Asummeetria: MGC kasutab SMA(50) aga MNQ kasutab EMA(21) - 2.4x erinev
   reaktsioonikiirus. Sama luhiajaliste strateegiatega (5m/15m) on see pohhjendamatu.
   Tanane logi: MGC SMA(50) slope oli -7.80 ja -7.24 ajal mil MNQ EMA(21) naitas
   uptrendi - tulemus: 2 MGC SHORT tehingut laksid taide bullish turul (sig-3, sig-17).

2. Puuduvad instrumendid: NG, MCL ei ole HTF_CONFIG-s -> saavad vaikimisi MNQ
   seadistuse (EMA21) mis on energia instrumentide jaoks vale.


## Muutused - src/engine/signal_filters.py

### 1. HTF_CONFIG (read 138-145) - ASENDA kogu blokk

```python
HTF_CONFIG = {
    # Equity indices - kiire EMA, reageerib ~21 baariga
    "MNQ": {"ma_type": "ema", "ma_period": 21, "slope_bars": 3, "grace_bars": 4},
    "MES": {"ma_type": "ema", "ma_period": 21, "slope_bars": 3, "grace_bars": 4},
    "MYM": {"ma_type": "ema", "ma_period": 21, "slope_bars": 3, "grace_bars": 4},
    "M2K": {"ma_type": "ema", "ma_period": 21, "slope_bars": 3, "grace_bars": 4},
    # Metals - EMA(34): kiirem kui vana SMA(50), sujuvam kui EMA(21)
    # Pohjus: 5m/15m strateegiad vajavad HTF-i mis reageerib <34h, mitte 50h
    "MGC": {"ma_type": "ema", "ma_period": 34, "slope_bars": 4, "grace_bars": 5},
    "MSI": {"ma_type": "ema", "ma_period": 34, "slope_bars": 4, "grace_bars": 5},
    # Energy - EMA(34): natgas on volatile, vajab kiiremat HTF-i kui SMA(50)
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

1. test_mgc_uses_ema34
   assert HTF_CONFIG["MGC"]["ma_type"] == "ema"
   assert HTF_CONFIG["MGC"]["ma_period"] == 34

2. test_mnq_uses_ema21
   assert HTF_CONFIG["MNQ"]["ma_type"] == "ema"
   assert HTF_CONFIG["MNQ"]["ma_period"] == 21

3. test_ng_has_explicit_config
   assert "NG" in HTF_CONFIG

4. test_mcl_has_explicit_config
   assert "MCL" in HTF_CONFIG

5. test_all_active_strategies_classified
   Loe /home/brrr/brrr-printer2/data/strategy_library/*.json
   Filtreeri kus active == True, kogu unikaalne strategy_name list
   all_classified = TREND_STRATEGIES | MEAN_REV_STRATEGIES | BREAKOUT_STRATEGIES
   Kontrolli et iga nimi on all_classified sees
   Kui mitte -> assert False, f"Klassifitseerimata strateegia: {name}"

6. test_no_strategy_in_multiple_lists
   Iga strateegia max uhes listis - ei tohi olla kahes korraga


## Nouded

- Ainult signal_filters.py + uus tests/test_htf_config.py
- EI muuda filter_config.json (HTF_CONFIG on koodis, mitte jsonis)
- EI muuda uhtegi teist parameetrit (thresholds, mode, atr jne)
- Engine restart pole vajalik - muutused joustuvad jargmisel signaalil
  (SignalFilterEngine.__init__ loeb HTF_CONFIG moodulist, mitte failist)

## Verification

```bash
cd /home/brrr/brrr-printer2
python -m pytest tests/test_htf_config.py -v
```

Eduka tulemusena peaks MGC jargmine signaal logima:
  HTF Trend: HTF UP/DOWN (EMA(34) slope ...) - mitte enam SMA(50)
