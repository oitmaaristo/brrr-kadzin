WO-SLTP flux:c498sgz P1 branch:auto-claude/wo-sltp-single-source
PROBLEEM: 10 erinevat hardcoded SL/TP väärtust. Lahendus: bracket_calculations.py = single source DEFAULT_SL=0.75 DEFAULT_TP=3.0. Kustuta engine.py 66-67, sync sltp_config.py, signal_generator.py fallbackid, position_monitor.py rida 1226.
