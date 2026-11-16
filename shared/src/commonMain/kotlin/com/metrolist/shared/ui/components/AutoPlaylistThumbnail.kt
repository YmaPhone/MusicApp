package com.metrolist.shared.ui.components

import androidx.compose.foundation.Image
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.layout.ContentScale
import com.metrolist.shared.generated.resources.Res
import com.metrolist.shared.generated.resources.logo
import org.jetbrains.compose.resources.painterResource

const val AUTO_PLAYLIST_ICON_PREFIX = "auto_playlist_icon_"
const val AUTO_PLAYLIST_ICON_LIKED = "auto_playlist_icon_liked"
const val AUTO_PLAYLIST_ICON_DOWNLOADED = "auto_playlist_icon_downloaded"
const val AUTO_PLAYLIST_ICON_TOP100 = "auto_playlist_icon_top100"
const val AUTO_PLAYLIST_ICON_UPLOADED = "auto_playlist_icon_uploaded"
const val AUTO_PLAYLIST_ICON_CACHED = "auto_playlist_icon_cached"

fun String?.isAutoPlaylistIcon(): Boolean = this?.startsWith(AUTO_PLAYLIST_ICON_PREFIX) == true

@Composable
fun AutoPlaylistThumbnail(
    iconIdentifier: String?,
    modifier: Modifier = Modifier,
    shape: Shape = RectangleShape,
) {
    Image(
        painter = painterResource(Res.drawable.logo),
        contentDescription = null,
        modifier = modifier.clip(shape),
        contentScale = ContentScale.Crop,
    )
}
