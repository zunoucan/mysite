package com.tokyohousing.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.tokyohousing.data.model.HousingListing
import com.tokyohousing.data.model.Ward
import com.tokyohousing.viewmodel.ListingsViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ListingsScreen(
    onListingClick: (Int) -> Unit,
    viewModel: ListingsViewModel = hiltViewModel(),
) {
    val state by viewModel.uiState.collectAsState()
    var showFilterSheet by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("東京23区 区立住宅") },
                actions = {
                    IconButton(onClick = { showFilterSheet = true }) {
                        Icon(Icons.Default.FilterList, contentDescription = "絞り込み")
                    }
                    IconButton(onClick = viewModel::loadListings) {
                        Icon(Icons.Default.Refresh, contentDescription = "更新")
                    }
                },
            )
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            // 区フィルターチップ
            WardFilterRow(
                wards = state.wards,
                selectedWardCode = state.selectedWardCode,
                onWardSelected = viewModel::setWardFilter,
            )

            when {
                state.isLoading -> Box(
                    Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center,
                ) { CircularProgressIndicator() }

                state.error != null -> ErrorCard(
                    message = state.error!!,
                    onRetry = viewModel::loadListings,
                )

                state.listings.isEmpty() -> EmptyState()

                else -> LazyColumn(
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    items(state.listings, key = { it.id }) { listing ->
                        ListingCard(listing = listing, onClick = { onListingClick(listing.id) })
                    }
                }
            }
        }
    }
}

@Composable
private fun WardFilterRow(
    wards: List<Ward>,
    selectedWardCode: String?,
    onWardSelected: (String?) -> Unit,
) {
    LazyRow(
        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        item {
            FilterChip(
                selected = selectedWardCode == null,
                onClick = { onWardSelected(null) },
                label = { Text("全区") },
            )
        }
        items(wards) { ward ->
            FilterChip(
                selected = selectedWardCode == ward.code,
                onClick = { onWardSelected(if (selectedWardCode == ward.code) null else ward.code) },
                label = { Text(ward.nameJa) },
            )
        }
    }
}

@Composable
fun ListingCard(listing: HousingListing, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Default.Home,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = listing.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                )
            }
            Spacer(Modifier.height(8.dp))
            Text(
                text = listing.address,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                listing.layout?.let { InfoChip(label = it) }
                listing.floorAreaSqm?.let { InfoChip(label = "%.1f㎡".format(it)) }
            }
            Spacer(Modifier.height(8.dp))
            listing.rentYen?.let { rent ->
                Text(
                    text = "家賃 ${"%,d".format(rent)}円/月",
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.SemiBold,
                )
            }
            listing.applicationEnd?.let { end ->
                Text(
                    text = "募集締切: $end",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error,
                )
            }
        }
    }
}

@Composable
private fun InfoChip(label: String) {
    Surface(
        shape = MaterialTheme.shapes.small,
        color = MaterialTheme.colorScheme.secondaryContainer,
    ) {
        Text(
            text = label,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelSmall,
        )
    }
}

@Composable
private fun ErrorCard(message: String, onRetry: () -> Unit) {
    Column(
        Modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Text(text = message, color = MaterialTheme.colorScheme.error)
        Spacer(Modifier.height(16.dp))
        Button(onClick = onRetry) { Text("再試行") }
    }
}

@Composable
private fun EmptyState() {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Text("現在募集中の住宅はありません", color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}
