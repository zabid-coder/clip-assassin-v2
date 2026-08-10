[Setup]
AppId={{7B8C9D2E-3F4A-5B6C-7D8E-9F0A1B2C3D4E}
AppName=Clip Assassin
AppVersion=2.0.1
AppPublisher=ZabidStudio
DefaultDirName={autopf}\Clip Assassin
DefaultGroupName=Clip Assassin
OutputDir=dist
OutputBaseFilename=Clip_Assassin_v2.0.1_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
SetupIconFile={#}\icon.ico
UninstallDisplayIcon={app}\Clip Assassin.exe

[Files]
Source: "dist\Clip Assassin\Clip Assassin.exe"; DestDir: "{app}"
Source: "dist\Clip Assassin\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs
Source: "frontend\dist\*"; DestDir: "{app}\frontend\dist"; Flags: recursesubdirs
Source: "presets\*"; DestDir: "{app}\presets"; Flags: recursesubdirs
Source: "templates\*"; DestDir: "{app}\templates"; Flags: recursesubdirs

[Icons]
Name: "{group}\Clip Assassin"; Filename: "{app}\Clip Assassin.exe"
Name: "{autodesktop}\Clip Assassin"; Filename: "{app}\Clip Assassin.exe"

[Run]
Filename: "{app}\Clip Assassin.exe"; Description: "{cm:LaunchProgram,Clip Assassin}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
end;
