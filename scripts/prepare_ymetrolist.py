#!/usr/bin/env python3
"""Apply YMetrolist-specific branding and updater configuration after syncing upstream."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return source.replace(old, new, 1)


# Set the installed app version to the upstream release being built.
gradle_properties = read("gradle.properties")
gradle_properties, version_changes = re.subn(
    r"(?m)^appVersion=.*$",
    "appVersion=14.0.1",
    gradle_properties,
)
if version_changes != 1:
    raise SystemExit(f"gradle.properties: expected one appVersion entry, found {version_changes}")
write("gradle.properties", gradle_properties)

# Direct in-app updates to YMetrolist's own GitHub releases, not the upstream app.
update_path = "androidApp/src/main/kotlin/com/metrolist/android/update/AppUpdateManager.kt"
update_manager = read(update_path)
update_manager = replace_once(
    update_manager,
    'private const val RELEASES_URL = "https://api.github.com/repos/MetrolistGroup/Metrolist/releases?per_page=50"',
    'private const val RELEASES_URL = "https://api.github.com/repos/YmaPhone/MusicApp/releases?per_page=50"',
    "release repository",
)
update_manager, cache_changes = re.subn(
    r'(?m)^private const val CACHE_SOURCE = "[^"]+"$',
    'private const val CACHE_SOURCE = "github-releases-ymetrolist-v1"',
    update_manager,
)
if cache_changes != 1:
    raise SystemExit(f"AppUpdateManager: expected one CACHE_SOURCE, found {cache_changes}")
preferred_pattern = r"(private val PREFERRED_APK_NAMES =\s*listOf\(\s*)"
if '"YMetrolist.apk"' not in update_manager:
    update_manager, preferred_changes = re.subn(
        preferred_pattern,
        r'\1        "YMetrolist.apk",\n',
        update_manager,
        count=1,
    )
    if preferred_changes != 1:
        raise SystemExit("AppUpdateManager: could not add YMetrolist.apk to preferred update assets")
write(update_path, update_manager)

# Replace the upstream credits/community/metadata panel with the requested YMetrolist text.
about_path = "shared/src/commonMain/kotlin/com/metrolist/shared/ui/screens/AboutScreen.kt"
about_screen = read(about_path)
start_marker = "    ) { paddingValues ->"
end_marker = "\n\n    selectedContributor?.let"
start = about_screen.find(start_marker, about_screen.find("fun AboutScreen("))
end = about_screen.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit("AboutScreen: could not locate the main content block")
replacement = """    ) { paddingValues ->
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(contentPadding)
                    .padding(bottom = bottomInset),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween,
        ) {
            Column(
                modifier = Modifier.fillMaxWidth().weight(1f),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
            ) {
                Surface(
                    onClick = ::handleLogoClick,
                    shape = RoundedCornerShape(28.dp),
                    color = colorScheme.primaryContainer,
                    modifier = Modifier.size(112.dp),
                ) {
                    Image(
                        painter = logo,
                        contentDescription = appName.ifBlank { stringResource(Res.string.app_name) },
                        colorFilter = ColorFilter.tint(colorScheme.onPrimaryContainer, BlendMode.SrcIn),
                        modifier = Modifier.padding(12.dp),
                    )
                }

                Spacer(Modifier.height(20.dp))

                Text(
                    text = appName.ifBlank { stringResource(Res.string.app_name) },
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = colorScheme.onSurface,
                    textAlign = TextAlign.Center,
                )

                Spacer(Modifier.height(24.dp))

                Text(
                    text = "נערך על ידי Yma בסייעתא דשמייא",
                    style = MaterialTheme.typography.titleMedium,
                    color = colorScheme.onSurface,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth(),
                )
            }

            Text(
                text = "הפרויקט הזה תומך בישראל",
                style = MaterialTheme.typography.labelSmall,
                color = colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }"""
about_screen = about_screen[:start] + replacement + about_screen[end:]
write(about_path, about_screen)

print("YMetrolist 14.0.1 branding and updater settings prepared.")
