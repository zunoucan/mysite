package com.tokyohousing.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.tokyohousing.data.model.HousingListing
import com.tokyohousing.data.model.Ward
import com.tokyohousing.viewmodel.ListingsViewModel

private val EXTRA_WARD_CODES = setOf("toei", "jkk", "ur")

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
                title = { Text("東京 公営・公社住宅") },
                actions = {
                    IconButton(onClick = { showFilterSheet = true }) {
                        Icon(Icons.Default.FilterList, contentDescription = "絞り込み・並び替え")
                    }
                    IconButton(onClick = viewModel::loadListings) {
                        Icon(Icons.Default.Refresh, contentDescription = "更新")
                    }
                },
            )
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            WardFilterRow(
                wards = state.wards,
                selectedWardCode = state.selectedWardCode,
                onWardSelected = viewModel::setWardFilter,
            )

            // アクティブなフィルター表示
            val hasFilter = state.selectedLayout != null || state.minRent != null ||
                            state.maxRent != null || state.sortBy != null
            if (hasFilter) {
                Row(
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    val labels = buildList {
                        state.sortBy?.let { add(sortLabel(it)) }
                        state.selectedLayout?.let { add(it) }
                        state.minRent?.let { add("${it / 10000}万円〜") }
                        state.maxRent?.let { add("〜${it / 10000}万円") }
                    }
                    Text(
                        text = "条件: ${labels.joinToString("　")}",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.primary,
                    )
                    TextButton(onClick = viewModel::clearFilters) { Text("クリア") }
                }
            }

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

                else -> {
                    Text(
                        text = "${state.listings.size}件",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 2.dp),
                    )
                    LazyColumn(
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

    if (showFilterSheet) {
        FilterBottomSheet(
            currentLayout = state.selectedLayout,
            currentMinRent = state.minRent,
            currentMaxRent = state.maxRent,
            currentSortBy = state.sortBy,
            onApply = { layout, minRent, maxRent, sortBy ->
                viewModel.applyFilters(layout, minRent, maxRent, sortBy)
                showFilterSheet = false
            },
            onDismiss = { showFilterSheet = false },
        )
    }
}

@Composable
private fun WardFilterRow(
    wards: List<Ward>,
    selectedWardCode: String?,
    onWardSelected: (String?) -> Unit,
) {
    val wardOnly = wards.filter { it.code !in EXTRA_WARD_CODES }
    val extraSources = wards.filter { it.code in EXTRA_WARD_CODES }

    LazyRow(
        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        item {
            FilterChip(
                selected = selectedWardCode == null,
                onClick = { onWardSelected(null) },
                label = { Text("すべて") },
            )
        }
        items(wardOnly) { ward ->
            FilterChip(
                selected = selectedWardCode == ward.code,
                onClick = { onWardSelected(if (selectedWardCode == ward.code) null else ward.code) },
                label = { Text(ward.nameJa) },
            )
        }
        if (extraSources.isNotEmpty()) {
            item {
                VerticalDivider(
                    modifier = Modifier
                        .height(32.dp)
                        .padding(horizontal = 4.dp),
                )
            }
            items(extraSources) { src ->
                FilterChip(
                    selected = selectedWardCode == src.code,
                    onClick = { onWardSelected(if (selectedWardCode == src.code) null else src.code) },
                    label = { Text(src.nameJa) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = MaterialTheme.colorScheme.tertiaryContainer,
                        selectedLabelColor = MaterialTheme.colorScheme.onTertiaryContainer,
                    ),
                )
            }
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
            // 住所を一番目立つ位置に
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Default.Home,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(Modifier.width(6.dp))
                Text(
                    text = listing.address.ifBlank { listing.name },
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                )
            }
            // 募集名はサブテキスト
            if (listing.address.isNotBlank()) {
                Spacer(Modifier.height(2.dp))
                Text(
                    text = listing.name,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Spacer(Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listing.layout?.let { InfoChip(label = it) }
                listing.floorAreaSqm?.let { InfoChip(label = "%.1f㎡".format(it)) }
                sourceLabel(listing.wardCode)?.let { InfoChip(label = it, secondary = true) }
            }
            listing.rentYen?.let { rent ->
                Spacer(Modifier.height(6.dp))
                Text(
                    text = "家賃 ${"%,d".format(rent)}円/月",
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.SemiBold,
                )
            }
            listing.applicationEnd?.let { end ->
                Spacer(Modifier.height(2.dp))
                Text(
                    text = "締切: $end",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error,
                )
            }
        }
    }
}

private fun sourceLabel(wardCode: String): String? = when (wardCode) {
    "toei" -> "都営"
    "jkk"  -> "JKK"
    "ur"   -> "UR"
    else   -> null
}

private fun sortLabel(sortBy: String): String = when (sortBy) {
    "rent_asc"      -> "家賃安い順"
    "rent_desc"     -> "家賃高い順"
    "end_date_asc"  -> "締切近い順"
    "area_desc"     -> "面積広い順"
    else            -> "新着順"
}

@Composable
private fun InfoChip(label: String, secondary: Boolean = false) {
    Surface(
        shape = MaterialTheme.shapes.small,
        color = if (secondary) MaterialTheme.colorScheme.tertiaryContainer
                else MaterialTheme.colorScheme.secondaryContainer,
    ) {
        Text(
            text = label,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelSmall,
            color = if (secondary) MaterialTheme.colorScheme.onTertiaryContainer
                    else MaterialTheme.colorScheme.onSecondaryContainer,
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FilterBottomSheet(
    currentLayout: String?,
    currentMinRent: Int?,
    currentMaxRent: Int?,
    currentSortBy: String?,
    onApply: (String?, Int?, Int?, String?) -> Unit,
    onDismiss: () -> Unit,
) {
    var draftLayout by remember { mutableStateOf(currentLayout) }
    var draftMinRent by remember { mutableStateOf(currentMinRent?.toString() ?: "") }
    var draftMaxRent by remember { mutableStateOf(currentMaxRent?.toString() ?: "") }
    var draftSortBy by remember { mutableStateOf(currentSortBy) }

    val layouts = listOf("1K", "1DK", "1LDK", "2K", "2DK", "2LDK", "3DK", "3LDK")
    val sortOptions = listOf(
        null to "新着順",
        "rent_asc" to "家賃：安い順",
        "rent_desc" to "家賃：高い順",
        "end_date_asc" to "締切日：近い順",
        "area_desc" to "面積：広い順",
    )

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp)
                .padding(bottom = 32.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Text("並び替え", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(sortOptions) { (value, label) ->
                    FilterChip(
                        selected = draftSortBy == value,
                        onClick = { draftSortBy = value },
                        label = { Text(label) },
                    )
                }
            }

            HorizontalDivider()
            Text("間取り", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(layouts) { layout ->
                    FilterChip(
                        selected = draftLayout == layout,
                        onClick = { draftLayout = if (draftLayout == layout) null else layout },
                        label = { Text(layout) },
                    )
                }
            }

            HorizontalDivider()
            Text("家賃範囲", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = draftMinRent,
                    onValueChange = { draftMinRent = it },
                    label = { Text("下限（円）") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                )
                OutlinedTextField(
                    value = draftMaxRent,
                    onValueChange = { draftMaxRent = it },
                    label = { Text("上限（円）") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                )
            }

            Button(
                onClick = {
                    onApply(
                        draftLayout,
                        draftMinRent.toIntOrNull(),
                        draftMaxRent.toIntOrNull(),
                        draftSortBy,
                    )
                },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("この条件で検索")
            }
        }
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
