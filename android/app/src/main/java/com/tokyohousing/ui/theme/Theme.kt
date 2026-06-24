package com.tokyohousing.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF1A56A0),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFD3E4FF),
    secondary = Color(0xFF2E7D32),
    secondaryContainer = Color(0xFFC8E6C9),
    background = Color(0xFFF8F9FA),
    surface = Color.White,
    error = Color(0xFFB00020),
)

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFF90CAF9),
    onPrimary = Color(0xFF003258),
    primaryContainer = Color(0xFF004880),
    secondary = Color(0xFFA5D6A7),
    secondaryContainer = Color(0xFF1B5E20),
    background = Color(0xFF121212),
    surface = Color(0xFF1E1E1E),
)

@Composable
fun TokyoHousingTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit,
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        content = content,
    )
}
