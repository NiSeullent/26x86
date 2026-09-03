#!/usr/bin/env python3
"""
Build-Project.command: Generate 26x86.app and 26x86.pkg
Optimiert für Sicherheit und Stabilität.
"""

import os
import re
import sys
import time
import argparse
import subprocess
from pathlib import Path

# Fix: Force the execution directory immediately before importing local modules. 
# This guarantees that 'ci_tooling' looks for assets in the right relative path.
SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)

# Import der internen Module
from ci_tooling.build_modules import (
    application,
    disk_images,
    package,
    sign_notarize
)

def check_file_exists(path: Path) -> None:
    if not path.exists():
        print(f"Fehler: Erwartete Datei/Verzeichnis nicht gefunden: {path}")
        print(f"Error: Expected file/directory not found: {path}")
        sys.exit(3)

def available_codesigning_identities() -> list:
    """
    Return (SHA-1 hash, name) for every valid code signing identity in the keychain

    'security find-identity -v' already filters out expired or otherwise unusable
    certificates. A self signed "Code Signing" certificate made in Keychain Access shows
    up here exactly like a Developer ID one.
    """
    if sys.platform != "darwin":
        return []

    try:
        result = subprocess.run(
            ["/usr/bin/security", "find-identity", "-v", "-p", "codesigning"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as e:
        print(f"Warnung: Signatur-Identitaeten konnten nicht abgefragt werden: {e}")
        print(f"Warning: could not query signing identities: {e}")
        return []

    identities = []
    for line in result.stdout.splitlines():
        # "security find-identity" haengt bei nicht vertrauenswuerdigen Zertifikaten
        # eine Statusmeldung an, z.B. (CSSMERR_TP_NOT_TRUSTED). Ein selbst signiertes
        # Zertifikat ist damit trotzdem brauchbar: das Helper Tool vergleicht nur die
        # Zertifikatsketten und fuehrt keine Trust-Pruefung durch.
        #
        # "security find-identity" appends a status note for certificates that are not
        # trusted, e.g. (CSSMERR_TP_NOT_TRUSTED). A self signed certificate still works:
        # the helper tool only compares certificate chains and runs no trust evaluation.
        match = re.match(r'\s*\d+\)\s+([0-9A-Fa-f]{40})\s+"(.+?)"\s*(\(CSSMERR_[A-Z_]+\))?\s*$', line)
        if match:
            identities.append((match.group(1), match.group(2), match.group(3)))
    return identities


def resolve_application_identity(requested: str, auto_detect: bool) -> str:
    """
    Decide which identity the app and the privileged helper tool get signed with

    Both must end up carrying the same certificate: at runtime the helper compares its own
    certificate chain against its parent process' chain (ci_tooling/privileged_helper_tool/main.m)
    and refuses to run anything as root when they differ. It runs no trust evaluation, so a
    self signed certificate satisfies it just as well as a Developer ID one - but an unsigned
    or ad-hoc signed build carries no certificates at all and can never pass.
    """
    requested = requested or os.environ.get("MACOS_SIGNING_IDENTITY")
    identities = available_codesigning_identities()

    if requested:
        # Only reject when the lookup actually returned something; an empty list means the
        # query failed or we are not on macOS, which is not evidence the identity is missing.
        if identities and not any(requested in (identity_hash, name) for identity_hash, name, _ in identities):
            print(f"Fehler: Keine gueltige Signatur-Identitaet gefunden fuer: {requested}")
            print(f"Error: no valid signing identity found matching: {requested}")
            print("       Available: " + (", ".join(f'"{name}"' for _, name, _ in identities) or "none"))
            sys.exit(3)
        return requested

    if auto_detect is False:
        return None

    if not identities:
        print("Hinweis: Kein Code-Signing-Zertifikat gefunden - App und Helper Tool bleiben unsigniert.")
        print("Note: no code signing certificate found, the app and helper tool stay unsigned.")
        print("      The privileged helper tool will refuse to run commands as root unless it was")
        print("      compiled with 'make debug' (ci_tooling/privileged_helper_tool/README.md).")
        print("      To sign locally, create a self signed certificate in Keychain Access:")
        print("      Certificate Assistant > Create a Certificate > Self Signed Root, type Code Signing.")
        return None

    if len(identities) > 1:
        print("Hinweis: Mehrere Code-Signing-Zertifikate gefunden - keines automatisch gewaehlt.")
        print("Note: multiple code signing certificates found, none picked automatically:")
        for _, name, _ in identities:
            print(f"      - {name}")
        print('      Pass --application-signing-identity "<name>" to choose one.')
        return None

    _, name, status = identities[0]
    print(f"Zertifikat automatisch gewaehlt: {name}")
    print(f"Automatically selected signing identity: {name}")
    if status:
        print(f"      Hinweis: Zertifikat ist nicht vertrauenswuerdig {status} - zum Signieren")
        print( "      genuegt das, das Helper Tool prueft nur die Zertifikatskette.")
        print(f"      Note: certificate is not trusted {status} - that is enough for signing,")
        print( "      the helper tool only compares certificate chains.")
    return name


def main() -> None:
    parser = argparse.ArgumentParser(description="Build 26x86 Suite", add_help=False)

    # Signing & Notarization
    parser.add_argument("--application-signing-identity", type=str, help="Application Signing Identity")
    parser.add_argument("--installer-signing-identity", type=str, help="Installer Signing Identity")
    parser.add_argument("--notarization-apple-id", type=str, help="Notarization Apple ID")
    parser.add_argument("--notarization-password", type=str, help="Notarization Password (Alternative: Env Var)")
    parser.add_argument("--notarization-team-id", type=str, help="Notarization Team ID")

    # CI/CD & Local Build Parameters
    parser.add_argument("--git-branch", type=str, default=None)
    parser.add_argument("--git-commit-url", type=str, default=None)
    parser.add_argument("--git-commit-date", type=str, default=None)
    parser.add_argument("--reset-dmg-cache", action="store_true")
    parser.add_argument("--reset-pyinstaller-cache", action="store_true")
    parser.add_argument("--no-auto-detect-identity", action="store_true", help="Never pick a signing identity from the keychain automatically")
    
    # Steps
    parser.add_argument("--run-as-individual-steps", action="store_true")
    parser.add_argument("--prepare-application", action="store_true")
    parser.add_argument("--prepare-package", action="store_true")
    parser.add_argument("--prepare-assets", action="store_true")

    args = parser.parse_args()

    # Passwort-Sicherheit: Umgebungsvariable hat Vorrang vor CLI-Argument
    notarization_password = os.environ.get("NOTARIZATION_PASSWORD") or args.notarization_password

    # Resolved once, so the app and the helper tool can never end up signed with two different
    # certificates - which would make the helper reject the app at runtime.
    application_signing_identity = resolve_application_identity(
        args.application_signing_identity,
        auto_detect=args.no_auto_detect_identity is False,
    )

    try:
        # 1. Assets
        if (args.run_as_individual_steps is False) or (args.run_as_individual_steps and args.prepare_assets):
            print("--- Generiere Disk Images ---")
            print("--- generate disk images ---")
            disk_images.GenerateDiskImages(args.reset_dmg_cache).generate()

        # 2. Application
        if (args.run_as_individual_steps is False) or (args.run_as_individual_steps and args.prepare_application):
            print("--- Signiere Helper Tool ---")
            print("--- Sign Helper Tool ---")
            sign_notarize.SignAndNotarize(
                path=Path("./ci_tooling/privileged_helper_tool/com.dortania.opencore-legacy-patcher.privileged-helper"),
                signing_identity=application_signing_identity,
                notarization_apple_id=args.notarization_apple_id,
                notarization_password=notarization_password,
                notarization_team_id=args.notarization_team_id,
            ).sign_and_notarize()

            print("--- Baue App ---")
            print("--- Building the app ---")
            application.GenerateApplication(
                reset_pyinstaller_cache=args.reset_pyinstaller_cache,
                git_branch=args.git_branch,
                git_commit_url=args.git_commit_url,
                git_commit_date=args.git_commit_date,
            ).generate()

            check_file_exists(Path("dist/26x86.app"))
            print("--- Signiere App ---")
            print("--- Sign the app ---")
            sign_notarize.SignAndNotarize(
                path=Path("dist/26x86.app"),
                signing_identity=application_signing_identity,
                notarization_apple_id=args.notarization_apple_id,
                notarization_password=notarization_password,
                notarization_team_id=args.notarization_team_id,
                entitlements=Path("./ci_tooling/entitlements/entitlements.plist"),
            ).sign_and_notarize()

        # 3. Packages
        if (args.run_as_individual_steps is False) or (args.run_as_individual_steps and args.prepare_package):
            print("--- Baue Packages ---")
            print("--- Build packages ---")
            package.GeneratePackage().generate()
            
            for pkg in ["26x86.pkg", "OpenCore-Patcher-Uninstaller.pkg"]:
                pkg_path = Path(f"dist/{pkg}")
                check_file_exists(pkg_path)
                print(f"--- Signiere {pkg} ---")
                print(f"--- Sign {pkg} ---")
                sign_notarize.SignAndNotarize(
                    path=pkg_path,
                    signing_identity=args.installer_signing_identity,
                    notarization_apple_id=args.notarization_apple_id,
                    notarization_password=notarization_password,
                    notarization_team_id=args.notarization_team_id,
                ).sign_and_notarize()

    except Exception as e:
        print(f"\n[!] Das Aufbauen des Apps hat abgebrochen aufgrund eines Fehlers: {e}")
        print(f"\n[!] Building the app stopped because of some error: {e}")
        sys.exit(3)

if __name__ == '__main__':
    _start = time.time()
    main()
    print(f"\nBuild script erfolgreich in {str(round(time.time() - _start, 2))} Sekunden abgeschlossen.")
    print(f"\nBuild script completed in {str(round(time.time() - _start, 2))} seconds.")
