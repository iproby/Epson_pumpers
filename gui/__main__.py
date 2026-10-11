#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entrypoint for `python -m gui`."""

from gui.app import EpsonPrinterApp

if __name__ == "__main__":
    app = EpsonPrinterApp()
    app.run()
