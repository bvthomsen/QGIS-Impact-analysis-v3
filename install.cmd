@echo on
set idir=impact_analysis
rmdir /s /q "%appdata%\QGIS\QGIS3\profiles\default\python\plugins\%idir%"
call .\%idir%\pyrcc5x.cmd
xcopy .\%idir%\* "%appdata%\QGIS\QGIS3\profiles\default\python\plugins\%idir%" /i /e /h /f 
pause
