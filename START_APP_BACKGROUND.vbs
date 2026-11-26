' ======================================================================
' Crop Recommendation & Yield Prediction System
' Silent Background Application Launcher (No Black Console Window)
' Bennett University • TEAM ROCKET (2025-2026)
' ======================================================================

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Resolve absolute path to project directory reliably
scriptFile = WScript.ScriptFullName
If InStr(scriptFile, "\") > 0 Then
    projectDir = fso.GetParentFolderName(scriptFile)
Else
    projectDir = fso.GetAbsolutePathName(".")
End If

venvPython = projectDir & "\venv\Scripts\pythonw.exe"
runPy = projectDir & "\run.py"

If Not fso.FileExists(venvPython) Then
    venvPython = projectDir & "\venv\Scripts\python.exe"
End If

If Not fso.FileExists(venvPython) Then
    venvPython = "python.exe"
End If

WshShell.CurrentDirectory = projectDir
cmd = "cmd.exe /c """"" & venvPython & """ """ & runPy & """"""
WshShell.Run cmd, 0, False

Set WshShell = Nothing
Set fso = Nothing
