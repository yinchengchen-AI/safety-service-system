@echo off
chcp 65001 >nul
title Safety Service - Frontend

cd /d %~dp0frontend
npm run dev
