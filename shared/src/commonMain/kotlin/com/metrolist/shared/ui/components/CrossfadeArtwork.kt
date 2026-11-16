package com.metrolist.shared.ui.components

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import com.metrolist.shared.ui.components.images.AsyncImage

@Suppress("UNUSED_PARAMETER")
@Composable
fun CrossfadeArtwork(
    currentUrl: String?,
    nextUrl: String?,
    progress: () -> Float,
    contentDescription: String?,
    contentScale: ContentScale,
    modifier: Modifier,
    animate: Boolean = true,
) {
    AsyncImage(
        url = currentUrl,
        contentDescription = contentDescription,
        contentScale = contentScale,
        modifier = modifier,
    )
}
