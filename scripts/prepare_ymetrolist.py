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
upstream_releases_url = 'private const val RELEASES_URL = "https://api.github.com/repos/MetrolistGroup/Metrolist/releases?per_page=50"'
ymetrolist_releases_url = 'private const val RELEASES_URL = "https://api.github.com/repos/YmaPhone/MusicApp/releases?per_page=50"'
if upstream_releases_url in update_manager:
    update_manager = update_manager.replace(upstream_releases_url, ymetrolist_releases_url, 1)
elif ymetrolist_releases_url not in update_manager:
    raise SystemExit("AppUpdateManager: expected upstream or YMetrolist release URL")
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


# Upstream 14.0.1 moved and expanded player code. Reapply the no-lyrics player
# policy on top of that version while leaving lyric providers/services intact.
player_path = "shared/src/commonMain/kotlin/com/metrolist/shared/ui/player/PlayerScreen.kt"
player = read(player_path)
player = player.replace(
    "    var showLyricsMenu by remember { mutableStateOf(false) }\n",
    "",
)
player = replace_once(
    player,
    "    val isTv = LocalIsTv.current\n",
    "    val isTv = LocalIsTv.current\n    LaunchedEffect(Unit) { viewModel.setLyricsVisible(false) }\n",
    "disable persisted player lyrics",
)
player, fetch_changes = re.subn(
    r"(?m)^    val shouldFetchLyrics = .*\n    val shouldLoadLyrics = .*?$",
    "    val shouldFetchLyrics = false\n    val shouldLoadLyrics = false",
    player,
)
if fetch_changes != 1:
    raise SystemExit(f"PlayerScreen: expected one lyrics-fetch policy block, found {fetch_changes}")
player = player.replace("onShowLyricsMenu = { showLyricsMenu = true }", "onShowLyricsMenu = {}")
player = player.replace(
    "onIsLyricsVisibleChange = { visible -> viewModel.setLyricsVisible(visible) }",
    "onIsLyricsVisibleChange = {}",
)
player = player.replace(
    "showLyrics = Settings.shared.showLyricsOnPlayer || canvasMinimalUi",
    "showLyrics = false",
)
player = player.replace(
    "visible = uiState.isLyricsVisible && showLyricsOffsetEditor",
    "visible = false",
)
player = player.replace("isLyricsVisible = uiState.isLyricsVisible", "isLyricsVisible = false")
player = player.replace("isLyricsVisible = uiState.isLyricsVisible,", "isLyricsVisible = false,")
player = re.sub(
    r"(?m)^\s*lyricsText = stringResource\(Res\.string\.lyrics\),\n",
    "",
    player,
)
player = re.sub(
    r"(?m)^\s*onLyricsClick = \{\n(?:.*\n){0,5}?\s*\},\n",
    "",
    player,
)
player = player.replace("onShowLyricsMenu = {\n                                                    hapticManager.perform(HapticEvent.PRESS)\n                                                    showLyricsMenu = true\n                                                },",
                        "onShowLyricsMenu = {},")
player = re.sub(
    r"(?ms)\n\s*PopupVisibility\(visible = showLyricsMenu\) \{\n\s*platform\.LyricsMenu\(.*?\n\s*\}\n",
    "\n",
    player,
)
if "showLyricsMenu" in player:
    raise SystemExit("PlayerScreen: showLyricsMenu references remain after disabling lyrics")
write(player_path, player)

# Keep Android intent/action identifiers namespaced under the YMetrolist package.
activity_path = "androidApp/src/main/kotlin/com/metrolist/android/MainActivity.kt"
activity = read(activity_path)
activity = activity.replace("com.metrolist.music.action.", "com.ymetrolist.music.action.")
write(activity_path, activity)

# The upstream collector uses a variant-to-filename map. Extend it for our
# optimized benchmark APK so release uploads and the in-app updater use one name.
collector_path = "scripts/collect_android_apks.py"
collector = read(collector_path)
collector, collector_changes = re.subn(
    r'(?m)^APK_NAMES = \{([^\n]+)\}$',
    lambda match: 'APK_NAMES = {' + match.group(1) + ', "benchmark": "YMetrolist.apk"}',
    collector,
)
if collector_changes != 1:
    raise SystemExit(f"APK collector: expected one APK_NAMES map, found {collector_changes}")
write(collector_path, collector)

# Retain the benchmark collector regression test after bringing in upstream tests.
test_path = "scripts/test_collect_android_apks.py"
test_source = read(test_path)
if "test_collects_optimized_benchmark_apk" not in test_source:
    benchmark_test = """    def test_collects_optimized_benchmark_apk(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.metadata(root, "benchmark", ["universal"])
            collect(root, root / "dist", "14.0.0-rc0", "benchmark")
            self.assertEqual({"YMetrolist.apk"}, {path.name for path in (root / "dist").iterdir()})
            self.assertEqual(b"universal", (root / "dist/YMetrolist.apk").read_bytes())

"""
    test_source = replace_once(
        test_source,
        "    def test_nightly_build_metadata_version(self):",
        benchmark_test + "    def test_nightly_build_metadata_version(self):",
        "benchmark APK regression test",
    )
    write(test_path, test_source)

print("YMetrolist 14.0.1 branding and updater settings prepared.")
