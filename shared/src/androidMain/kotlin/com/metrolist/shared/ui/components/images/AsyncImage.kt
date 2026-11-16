package com.metrolist.shared.ui.components.images

import androidx.compose.foundation.Image
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.layout.ContentScale
import com.metrolist.shared.generated.resources.Res
import com.metrolist.shared.generated.resources.logo
import org.jetbrains.compose.resources.painterResource

@Suppress("UNUSED_PARAMETER")
@Composable
actual fun AsyncImage(
    url: String?,
    modifier: Modifier,
    contentDescription: String?,
    contentScale: ContentScale,
    alignment: androidx.compose.ui.Alignment,
    shape: Shape?,
    error: Painter?,
    previewUrl: String?,
    saturation: Float,
) {
    Image(
        painter = painterResource(Res.drawable.logo),
        contentDescription = contentDescription,
        modifier = if (shape != null) modifier.clip(shape) else modifier,
        contentScale = contentScale,
        alignment = alignment,
    )
}
