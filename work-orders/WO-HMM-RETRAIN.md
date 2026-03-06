# WO-HMM-RETRAIN: HMM Treeningkava + Cron
P2 | scripts/retrain_hmm.py + crontab | Gatekeeper: Risto

Olukord:
HMM mudelid treeniti esimest korda 2026-03-06 WO-HMM01 kaudu.
Cron puudub - retrain_hmm.py on olemas aga keegi ei kutsu seda.
Mudelid: MGC_15m, MGC_60m, MNQ_15m, MNQ_60m

Mida teha:
1. Kontrolli retrain_hmm.py - kas 90p andmed on piisavad, kas koik 4 mudelit treenivad, lisa logimine (vahemik, baarid, konvergents)
2. Lisa cron: 0 2 * * * .../venv/bin/python .../scripts/retrain_hmm.py >> .../data/hmm_retrain.log 2>&1
3. Treeningaken 90 paeva OK. Ara kasuta andmeid nooremaid kui 1 paev.

Ei kuulu siia: HMM dashboard visualiseerimine (eraldi WO), HTF/RVOL/ORB (WO-FILTRID-UUED3)

Branch: auto-claude/wo-hmm-retrain
