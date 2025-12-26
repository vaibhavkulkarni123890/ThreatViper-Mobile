/* Rule Removed: Suspicious_PE_Header was too generic */

rule Suspicious_PowerShell {
    meta:
        description = "Detects obfuscated PowerShell scripts"
        severity = "Critical"
    strings:
        $s1 = "powershell" nocase
        $s2 = "-nop" nocase
        $s3 = "-w hidden" nocase
        $s4 = "IEX" nocase
        $s5 = "Invoke-Expression" nocase
        $b64 = "FromBase64String"
    condition:
        $s1 and ($s2 or $s3 or ($s4 and $b64) or ($s5 and $b64))
}

rule Ransomware_Indicators {
    meta:
        description = "Detects common ransomware ransom notes and extensions"
        severity = "Critical"
    strings:
        $n1 = "YOUR FILES ARE ENCRYPTED" nocase
        $n2 = "restore your files" nocase
        $n3 = "bitcoin" nocase
        $ext1 = ".crypt" nocase
        $ext2 = ".lock" nocase
    condition:
        2 of ($n*) or any of ($ext*)
}

rule Suspicious_Autorun {
    meta:
        description = "Detects autorun.inf files commonly used by USB malware"
        severity = "Medium"
    strings:
        $tag = "[autorun]" nocase
        $cmd = "open=" nocase
        $shl = "shell\\open\\command=" nocase
    condition:
        $tag and ($cmd or $shl)
}

rule Keylogger_Hooks {
    meta:
        description = "Detects API calls associated with keylogging"
        severity = "High"
    strings:
        $h1 = "SetWindowsHookEx" ascii
        $h2 = "GetAsyncKeyState" ascii
        $h3 = "GetForegroundWindow" ascii
    condition:
        all of them
}
