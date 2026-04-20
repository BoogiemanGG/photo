; ──────────────────────────────────────────────────────────────────
; PhotoStudioHub — Inno Setup Script
; Produces:  PhotoStudioHub-Setup-1.0.exe
;
; Requirements:
;   • Inno Setup 6.x  (https://jrsoftware.org/isinfo.php) — free
;   • PyInstaller dist/PhotoStudioHub/ folder already built
;
; Run (from project root):
;   ISCC installer\setup.iss
; ──────────────────────────────────────────────────────────────────

#define AppName      "PhotoStudioHub"
#define AppVersion   "1.0"
#define AppPublisher "PhotoStudioHub"
#define AppURL       "https://photostudiohub.netlify.app"
#define AppExeName   "PhotoStudioHub.exe"
#define BuildDir     "..\dist\PhotoStudioHub"

[Setup]
AppId={{B3F9A2D1-7E4C-4A8B-9F2E-1C5D8E3A6B7F}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=PhotoStudioHub-Setup-{#AppVersion}
#if FileExists("icon.ico")
SetupIconFile=icon.ico
#endif
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0

; Uninstall settings
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}

[Languages]
Name: "english";  MessagesFile: "compiler:Default.isl"
Name: "german";   MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon";    Description: "{cm:CreateDesktopIcon}";    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Application files from PyInstaller COLLECT output
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Visual C++ Redistributable (include vcredist if needed)
; Source: "vcredist_x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}";   Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";       Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Check Windows 10+ before install
function InitializeSetup(): Boolean;
begin
  Result := True;
  if not IsWin64 then begin
    MsgBox('PhotoStudioHub requires a 64-bit version of Windows 10 or later.', mbError, MB_OK);
    Result := False;
  end;
end;
