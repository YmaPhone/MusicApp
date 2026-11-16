package com.metrolist.shared.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.painter.Painter
import coil3.Image

internal data class LayerArt(
    val painter: Painter,
    val pixelWidth: Float?,
    val pixelHeight: Float?,
    val image: Image? = null,
)

@Composable
internal expect fun PlatformLiquidBackgroundCanvas(
    modifier: Modifier,
    activeArt: LayerArt,
    previousArt: LayerArt?,
    crossfadeAlpha: () -> Float,
    rotationTimeMs: () -> Long,
)

@Suppress("UNUSED_PARAMETER")
@Composable
fun LiquidBackground(
    artworkUrl: String?,
    modifier: Modifier = Modifier,
    isLyricsVisible: Boolean = false,
    animate: Boolean = true,
    isPlaying: Boolean = true,
    visible: Boolean = true,
) {
    Box(
        modifier = modifier.fillMaxSize().clipToBounds().background(Color.Black),
    )
}
