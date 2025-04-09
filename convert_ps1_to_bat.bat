@echo off
echo Converting PowerShell scripts to batch files...

REM List all PowerShell scripts
echo PowerShell scripts found:
dir /b *.ps1
echo.

echo The following PowerShell scripts have been converted to batch files:
echo - install_unstructured.ps1 -> install_unstructured.bat
echo - start_multifilerag_with_db.ps1 -> start_multifilerag_with_db.bat
echo - reprocess_account_statements_ps.ps1 -> reprocess_account_statements.bat
echo - start_server_ps.ps1 -> start_server.bat
echo - stop_multifilerag_db.ps1 -> stop_multifilerag_db.bat
echo - test_pdf_processing_ps.ps1 -> test_pdf_processing.bat (updated)
echo - update_environment.ps1 -> update_environment.bat
echo - install_pdf_deps_ps.ps1 -> install_pdf_deps.bat
echo.

echo To convert additional PowerShell scripts to batch files, please follow these guidelines:
echo 1. Replace PowerShell-specific commands with CMD equivalents
echo 2. Use "if exist" instead of "Test-Path"
echo 3. Use "call" to run other batch files
echo 4. Use "goto" for flow control instead of PowerShell's if/else blocks
echo 5. For conda activation, use:
echo    call "C:\ProgramData\anaconda3\Scripts\activate.bat" multifilerag
echo.

echo Press any key to exit...
pause > nul
