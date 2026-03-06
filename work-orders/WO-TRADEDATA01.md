# WO-TRADEDATA01: Trade andmete taeielikkus

**Prioriteet:** P1 | **Branch:** auto-claude/wo-tradedata01 | **Gatekeeper:** Risto

## PROBLEEM

1. close_reason alati MANUAL - SL/TP hitti ei detekteerita
2. strategy_id + timeframe puuduvad DB-st
3. DataHub TradeLogger surnud - avab oma WS TopStepX-ile, broker sulgeb (conflict), 0 kirjet

## ROOT CAUSE

DataHub avab paralleelse WebSocket TopStepX-ile, broker sulgeb kohe (Socket closed by server loop).
Engine _on_position() ja _on_bracket_fill() naevad koiki evente aga ei edasta TradeLogger-ile.

## LAHENDUS

### OSA 1: Lopeta DataHubi oma WebSocket

src/data_hub/hub.py:
- Lisa standalone_mode: bool = False
- Kui False: ara kaivita self.ws_client TopStepX-iga
- DataHub WS dashboard clientidele jaab alles

### OSA 2: Uhenda TradeLogger engine_wiring-iga

src/engine/engine_wiring.py:

INIT - lisa trade_logger initsialiseerimine:
  from src.data_hub.trade_logger import TradeLogger
  from src.data_hub.persistence import TradeDatabase
  self.trade_db = TradeDatabase(Path("data/datahub.db"))
  await self.trade_db.initialize()
  self.trade_logger = TradeLogger(db=self.trade_db)

_on_position() loppu:
  if self.trade_logger:
      asyncio.ensure_future(self.trade_logger.on_position_update(data))

_on_bracket_fill() loppu - set_strategy + resolve ID:
  if self.trade_logger and position.strategy_name:
      sid = self._resolve_strategy_id(position)
      self.trade_logger.set_strategy(position.symbol, position.strategy_name,
          json.dumps({"strategy_id": sid, "timeframe": getattr(position,"timeframe",None),
                      "sl": position.intended_sl, "tp": position.intended_tp}))

Helper:
  def _resolve_strategy_id(self, position) -> str:
      name = (position.strategy_name or "").lower().replace(" ","")
      sym = (position.symbol or "").lower()
      tf = getattr(position, "timeframe", None)
      if tf:
          c = f"{name}-{sym}-{tf}m-v1"
          if (Path("data/strategy_library") / f"{c}.json").exists(): return c
      return f"{name}-{sym}"

### OSA 3: MonitoredPosition

position_monitor.py dataclass lisa:
  strategy_id: str | None = None
  timeframe: int | None = None

engine_wiring.py bracket fill:
  position.strategy_id = self._resolve_strategy_id(position)
  position.timeframe = signal.timeframe

### OSA 4: DB migratsioon

position_storage.py IF NOT EXISTS:
  closed_positions + positions: strategy_id TEXT, timeframe INTEGER
  close_position() + save_position(): salvesta uued valjad

### OSA 5: close_reason

engine_wiring.py _on_order():
  status=2 + type=4 -> INTENDED_SL
  status=2 + type=1 -> INTENDED_TP
  type=2 (entry) -> return/skip
  Leia pos contract_id jargi, kutsu _close_position() oige reason-iga.

## ACCEPTANCE CRITERIA

- [ ] DataHub ei ava oma WS TopStepX-iga
- [ ] datahub.db trades taitub igal sulgemisel
- [ ] closed_positions.strategy_id = bollingerbreakout-mgc-5m-v1
- [ ] closed_positions.timeframe = 5/15/60
- [ ] close_reason: SL/TP/MANUAL oigesti
- [ ] Migration IF NOT EXISTS
- [ ] Min 6 unit testi

## EI TOHI

- Muuta DataHubi WS broadcasti dashboard clientidele
- Restartida engine ilma Risto loata
