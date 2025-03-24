#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------
# Created for: PolarE
# Dev line: PolarE
# Creation day: 03/03/2025
# Last change: 24/03/2025
#---------------------------------------------------------------------------


app_name = "POLAR"
app_version = "0.4.0_dev2"
app_lang = "es"


import app.magerit


modules = []
modules.append({'name': "Asset-Risk (ISO 27005, Magerit)", 'version':"beta1", 'date':"2025-03-03", 'mfile':"magerit", 'module':app.magerit.Magerit(app_lang)})

#export_data_support = False
#export_data_set = ['Assets']
