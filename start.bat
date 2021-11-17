@echo off

tasklist /fi "Image"
N:
cd "N:\ZBrock\Vorne\REST API\"
start pythonw guimain.pyw