# HMM — praegune vs ideaalne
Kirjutatud: 2026-03-06

## Praegu

Toetatud: MGC ja MNQ, TF 15m ja 60m.
Muu instrument = 2-state ADX fallback, ei ole HMM.
Muu TF (nt 30m) = langeb 15m defaultile, pole teadlik valik.
30m strateegiad ei tohiks aktiivsed olla.

Loogika:
60m on ulemus. Kui 60m high_vol > 0.7 -> blokeeri koik.
Kui 60m OK -> 15m otsustab entry timing.
3 seisundit: low_vol_trending, low_vol_ranging, high_vol.

## Ideaalne

Koik aktiivsed instrumendid saaksid oma mudeli (MGC, MNQ, MES jne).
TF hierarhia oleks selge ja teadlik, mitte defaulti peale langev:
  - 5m signaal: kasutab 5m + 15m mudelit
  - 15m signaal: kasutab 15m + 60m mudelit
  - 60m signaal: kasutab 60m + 1D mudelit
30m TF pole toetatud ja ei lisata.

Mudel teaks ise mis andmed ta saab ja mis TF-ga ta treenitud on.
Ei peaks hardcode-ima "kui muu TF siis 15m default".
