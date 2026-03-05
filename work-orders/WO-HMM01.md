# WO-HMM01: HMM Korralik Treening ja Set-Up
**P2** | brrr-printer2 src/engine/regime_detector.py | Gatekeeper: Risto

## Praegune seis (2026-03-05)
1 jagatud RegimeDetector, 2-state, 1 feature (log returns).
model.predict() koigi ajalooga = look-ahead bias oht.

## Nouded
4 mudelit: MGC-60m, MGC-15m, MNQ-60m, MNQ-15m
3 state: low_vol_trending / low_vol_ranging / high_vol
2 feature: log_returns + ATR_ratio, covariance_type=full
Online inference: incremental (iga baar +1 vaatlus, mitte koik ajaloolised)
Label-switching fix parast retrain (suurem variance = high_vol)
Retrain 1x/paev 02:00 EET, 90p andmed
Hierarhia: 60m varavaaht -> 15m entry timing

## Ulesoanded
1. get_regime_detector(symbol, tf) - eraldi instance per symbol+tf
2. GaussianHMM n_components=3, 2 features, full covariance
3. OnlineHMMFilter: incremental predict
4. Auto check_state_ordering() parast iga fit()
5. scripts/retrain_hmm.py - cron 02:00 EET
6. signal_generator: 60m high_vol blokeeri, 15m entry timing

## Testimine
MGC ja MNQ erinevad regime hinnangud samal hetkel.
