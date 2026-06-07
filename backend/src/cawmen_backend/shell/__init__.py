"""Imperative shell: all I/O lives here (see ADR-0008).

Holds the ports the pure core depends on — a ``StateStore`` for persistence and a
``TextProvider`` for narrative prose — plus Scenario loading from authored files.
"""
