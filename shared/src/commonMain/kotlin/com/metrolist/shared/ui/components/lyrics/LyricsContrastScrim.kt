package com.metrolist.shared.ui.components.lyrics

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.EnterTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.ColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ColorMatrix
import androidx.compose.ui.graphics.compositeOver
import androidx.compose.ui.graphics.luminance

internal fun lyricsContrastScrimAlpha(
    textColor: Color,
    backgrounds: List<Color>,
): Float {
    val textLuminance = textColor.luminance()

    fun readable(alpha: Float): Boolean =
        backgrounds.all { background ->
            val luminance =
                Color.Black
                    .copy(alpha = alpha)
                    .compositeOver(background)
                    .luminance()
            (textLuminance + 0.05f) / (luminance + 0.05f) >= 4.5f
        }

    if (readable(0f)) return 0f
    var low = 0f
    var high = 1f
    repeat(16) {
        val middle = (low + high) / 2f
        if (readable(middle)) high = middle else low = middle
    }
    return high
}

internal fun lyricsPaletteTextColor(
    scheme: ColorScheme,
    lightText: Boolean,
): Color =
    if (lightText) {
        if (scheme.primaryFixed.luminance() >= scheme.onPrimaryFixed.luminance()) scheme.primaryFixed else scheme.onPrimaryFixed
    } else {
        scheme.onPrimaryFixedVariant
    }

internal fun saturatedLyricsArtworkColor(
    color: Color,
    matrix: ColorMatrix,
): Color {
    val values = matrix.values

    fun channel(row: Int): Float =
        (values[row * 5] * color.red + values[row * 5 + 1] * color.green + values[row * 5 + 2] * color.blue).coerceIn(0f, 1f)
    return Color(channel(0), channel(1), channel(2), color.alpha)
}

@Suppress("UNUSED_PARAMETER")
@Composable
fun LyricsContrastScrim(
    backgroundColors: List<Color>,
    artworkUrl: String? = null,
    artworkScrimAlpha: Float = 0f,
    artworkWhiteAlpha: Float = 0f,
    artworkSaturation: Float = 1f,
    isLiquid: Boolean = false,
    visible: Boolean = true,
) {
    AnimatedVisibility(
        visible = visible,
        modifier = Modifier.fillMaxSize(),
        enter = EnterTransition.None,
        exit = fadeOut(tween(500)),
    ) {
        val textColor = resolveLyricsTextColor(Color.White)
        val alpha = lyricsContrastScrimAlpha(textColor, backgroundColors)
        if (alpha > 0f) Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = alpha)))
    }
}
