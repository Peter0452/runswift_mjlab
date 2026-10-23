"""The evolution loop (knowledge/architecture.md "Evolution loop").

outer     decides what to try: champion -> designer -> recipe -> gates -> pool ->
          judge -> verdict -> promote or record; escalates to the user after N
          non-improving verdicts (``outer.py``)
inner     tunes one recipe's continuous numbers while it trains (PBT exploit /
          explore, ``inner.py``)
state     single-writer, resume-safe JSON under experiments/evolution/ (``state.py``)
designers propose recipes (``designers/``)
"""
