/**
 * Metrolist Project (C) 2026
 * Licensed under GPL-3.0 | See git history for contributors
 */

package com.metrolist.android.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.os.Bundle
import android.view.View
import android.widget.RemoteViews
import com.metrolist.android.App
import com.metrolist.android.MainActivity
import com.metrolist.android.R
import com.metrolist.android.recognition.MusicRecognitionService
import com.metrolist.android.recognition.RecognitionLaunchActivity
import com.metrolist.android.recognition.RecognitionWidgetService
import com.metrolist.android.utils.launchAsync
import com.metrolist.shared.recognition.RecognitionStatus
import kotlinx.coroutines.CancellationException
import timber.log.Timber

class RecognizerWidgetReceiver : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray,
    ) {
        refresh(context)
    }

    override fun onAppWidgetOptionsChanged(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int,
        newOptions: Bundle,
    ) {
        super.onAppWidgetOptionsChanged(context, appWidgetManager, appWidgetId, newOptions)
        refresh(context)
    }

    private fun refresh(context: Context) {
        launchAsync {
            try {
                (context.applicationContext as App).startup.await()
                RecognizerWidgets.update(context)
            } catch (error: CancellationException) {
                throw error
            } catch (error: Exception) {
                Timber.e(error, "Failed to refresh recognizer widgets")
            }
        }
    }
}

object RecognizerWidgets {
    private const val TINY_MAX_WIDTH_DP = 110

    suspend fun update(context: Context) {
        val appWidgetManager = AppWidgetManager.getInstance(context) ?: return
        val widgetIds = appWidgetManager.getAppWidgetIds(ComponentName(context, RecognizerWidgetReceiver::class.java))
        if (widgetIds.isEmpty()) return
        val status = MusicRecognitionService.status.value
        val artwork = loadMetrolistLogo(context)
        widgetIds.forEach { widgetId ->
            val minWidth = appWidgetManager.getAppWidgetOptions(widgetId).getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH)
            val compact = minWidth in 1 until TINY_MAX_WIDTH_DP
            val views =
                if (compact) {
                    RemoteViews(context.packageName, R.layout.widget_recognizer_tiny)
                } else {
                    RemoteViews(context.packageName, R.layout.widget_recognizer).also { bindDetails(context, it, status, artwork) }
                }
            bindMic(context, views, status, compact)
            appWidgetManager.updateAppWidget(widgetId, views)
        }
    }

    private fun bindMic(
        context: Context,
        views: RemoteViews,
        status: RecognitionStatus,
        compact: Boolean,
    ) {
        val active = status is RecognitionStatus.Listening || status is RecognitionStatus.Processing
        val showResult = compact && status is RecognitionStatus.Success
        views.setContentDescription(
            R.id.widget_recognizer_mic_icon,
            context.getString(
                when {
                    active -> R.string.menu_stop
                    showResult -> R.string.widget_recognizer_open_result
                    else -> R.string.widget_recognizer_mic_desc
                },
            ),
        )
        views.setViewVisibility(R.id.widget_recognizer_progress, if (active) View.VISIBLE else View.GONE)
        views.setInt(
            R.id.widget_recognizer_mic_button,
            "setBackgroundResource",
            if (active) R.drawable.widget_mic_active_bg else R.drawable.widget_mic_bg,
        )
        views.setImageViewResource(
            R.id.widget_recognizer_mic_icon,
            when {
                active -> R.drawable.ic_widget_mic_active
                showResult -> R.drawable.ic_widget_play
                else -> R.drawable.ic_widget_mic
            },
        )
        val micIntent =
            if (showResult) {
                openRecognitionIntent(context)
            } else {
                PendingIntent.getActivity(
                    context,
                    REQUEST_TOGGLE,
                    Intent(context, RecognitionLaunchActivity::class.java).setAction(RecognitionWidgetService.ACTION_TOGGLE),
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
                )
            }
        views.setOnClickPendingIntent(R.id.widget_recognizer_mic_container, micIntent)
    }

    private fun bindDetails(
        context: Context,
        views: RemoteViews,
        status: RecognitionStatus,
        artwork: Bitmap?,
    ) {
        val (title, subtitle) =
            when (status) {
                RecognitionStatus.Ready -> {
                    context.getString(R.string.widget_recognizer_tap_to_search) to null
                }

                RecognitionStatus.Listening -> {
                    context.getString(R.string.listening) to null
                }

                RecognitionStatus.Processing -> {
                    context.getString(R.string.widget_recognizer_processing) to null
                }

                is RecognitionStatus.Success -> {
                    status.result.title to
                        if (status.historySaved) status.result.artist else context.getString(R.string.recognition_history_save_failed)
                }

                is RecognitionStatus.NoMatch -> {
                    context.getString(R.string.widget_recognizer_no_match) to null
                }

                is RecognitionStatus.Error -> {
                    context.getString(R.string.recognition_failed) to status.message
                }
            }
        views.setTextViewText(R.id.widget_recognizer_title, title)
        views.setTextViewText(R.id.widget_recognizer_subtitle, subtitle.orEmpty())
        views.setViewVisibility(R.id.widget_recognizer_subtitle, if (subtitle.isNullOrBlank()) View.GONE else View.VISIBLE)
        views.setViewVisibility(R.id.widget_recognizer_album_art, if (artwork != null) View.VISIBLE else View.GONE)
        artwork?.let { views.setImageViewBitmap(R.id.widget_recognizer_album_art, it) }
        val openIntent = openRecognitionIntent(context)
        views.setOnClickPendingIntent(R.id.widget_recognizer_text_area, openIntent)
        views.setOnClickPendingIntent(R.id.widget_recognizer_album_art, openIntent)
    }

    private fun openRecognitionIntent(context: Context): PendingIntent =
        PendingIntent.getActivity(
            context,
            REQUEST_OPEN,
            Intent(context, MainActivity::class.java)
                .setAction(MainActivity.ACTION_RECOGNITION)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )

    private fun loadMetrolistLogo(context: Context): Bitmap {
        val drawable = context.packageManager.getApplicationIcon(context.packageName)
        val bitmap = Bitmap.createBitmap(240, 240, Bitmap.Config.ARGB_8888)
        Canvas(bitmap).also { canvas ->
            drawable.setBounds(0, 0, 240, 240)
            drawable.draw(canvas)
        }
        return bitmap
    }

    private const val REQUEST_TOGGLE = 700
    private const val REQUEST_OPEN = 701
}
