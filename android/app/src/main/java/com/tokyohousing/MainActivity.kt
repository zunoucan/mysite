package com.tokyohousing

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.tokyohousing.ui.screens.DetailScreen
import com.tokyohousing.ui.screens.ListingsScreen
import com.tokyohousing.ui.screens.ProfileScreen
import com.tokyohousing.ui.theme.TokyoHousingTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            TokyoHousingTheme {
                TokyoHousingNavGraph()
            }
        }
    }
}

@Composable
fun TokyoHousingNavGraph() {
    val navController = rememberNavController()
    val currentRoute by navController.currentBackStackEntryAsState()

    val bottomNavItems = listOf(
        BottomNavItem("listings", "住宅一覧", Icons.Default.Home),
        BottomNavItem("profile", "プロフィール", Icons.Default.Person),
    )

    Scaffold(
        bottomBar = {
            val route = currentRoute?.destination?.route
            if (route != null && !route.startsWith("detail")) {
                NavigationBar {
                    bottomNavItems.forEach { item ->
                        NavigationBarItem(
                            selected = route == item.route,
                            onClick = {
                                navController.navigate(item.route) {
                                    popUpTo("listings") { saveState = true }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = { Icon(item.icon, contentDescription = item.label) },
                            label = { Text(item.label) },
                        )
                    }
                }
            }
        }
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = "listings",
            modifier = Modifier.padding(padding),
        ) {
            composable("listings") {
                ListingsScreen(onListingClick = { id -> navController.navigate("detail/$id") })
            }
            composable(
                route = "detail/{listingId}",
                arguments = listOf(navArgument("listingId") { type = NavType.IntType }),
            ) {
                DetailScreen(onBack = navController::popBackStack)
            }
            composable("profile") {
                ProfileScreen()
            }
        }
    }
}

private data class BottomNavItem(
    val route: String,
    val label: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector,
)
