package com.tokyohousing.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.OpenInBrowser
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.tokyohousing.data.model.HousingListing
import com.tokyohousing.viewmodel.DetailViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DetailScreen(
    onBack: () -> Unit,
    viewModel: DetailViewModel = hiltViewModel(),
) {
    val state by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(state.listing?.name ?: "詳細") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "戻る")
                    }
                },
            )
        }
    ) { padding ->
        when {
            state.isLoading -> Box(
                Modifier.fillMaxSize().padding(padding),
                contentAlignment = Alignment.Center
            ) { CircularProgressIndicator() }

            state.listing != null -> {
                val listing = state.listing!!
                Column(
                    Modifier
                        .fillMaxSize()
                        .padding(padding)
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                ) {
                    // 基本情報カード
                    InfoSection(title = "物件情報") {
                        InfoRow("住所", listing.address)
                        listing.layout?.let { InfoRow("間取り", it) }
                        listing.floorAreaSqm?.let { InfoRow("床面積", "%.1f㎡".format(it)) }
                        listing.floorLevel?.let { InfoRow("所在階", "${it}階") }
                        listing.yearBuilt?.let { InfoRow("建築年", "${it}年") }
                    }

                    // 家賃情報カード
                    InfoSection(title = "家賃・費用") {
                        listing.rentYen?.let { InfoRow("家賃", "%,d円/月".format(it)) }
                        listing.managementFeeYen?.let { InfoRow("管理費", "%,d円/月".format(it)) }
                        listing.depositYen?.let { InfoRow("敷金", "%,d円".format(it)) }
                        if ((listing.rentYen ?: 0) + (listing.managementFeeYen ?: 0) > 0) {
                            InfoRow(
                                "月額合計",
                                "%,d円".format(listing.totalMonthlyYen),
                                emphasize = true,
                            )
                        }
                    }

                    // 応募期間
                    InfoSection(title = "応募情報") {
                        listing.applicationStart?.let { InfoRow("受付開始", it) }
                        listing.applicationEnd?.let { InfoRow("締切日", it) }
                        listing.lotteryDate?.let { InfoRow("抽選日", it) }
                        listing.moveInDate?.let { InfoRow("入居予定", it) }
                    }

                    // 入居者条件
                    listing.eligibilityConditions?.let {
                        InfoSection(title = "入居者条件") {
                            Text(it, style = MaterialTheme.typography.bodyMedium)
                        }
                    }

                    // リンク
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        listing.detailUrl?.let { url ->
                            OutlinedButton(onClick = {
                                context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
                            }) {
                                Icon(Icons.Default.OpenInBrowser, contentDescription = null)
                                Spacer(Modifier.width(4.dp))
                                Text("詳細ページ")
                            }
                        }
                        if (listing.address.isNotBlank()) {
                            OutlinedButton(onClick = {
                                val query = Uri.encode(listing.address)
                                context.startActivity(
                                    Intent(Intent.ACTION_VIEW, Uri.parse("https://maps.google.com/?q=$query"))
                                )
                            }) {
                                Icon(Icons.Default.OpenInBrowser, contentDescription = null)
                                Spacer(Modifier.width(4.dp))
                                Text("地図で見る")
                            }
                        }
                    }

                    HorizontalDivider()

                    // 申請ボタン
                    ApplySection(
                        hasFormUrl = listing.applicationFormUrl != null,
                        isApplying = state.isApplying,
                        onFillPdf = { viewModel.apply(premiumToken = null) },
                        onAutoSubmit = { token -> viewModel.apply(premiumToken = token) },
                    )
                }
            }
        }
    }

    // 申請結果ダイアログ
    state.applyResult?.let { result ->
        AlertDialog(
            onDismissRequest = viewModel::clearApplyResult,
            icon = {
                if (result.success) Icon(Icons.Default.CheckCircle, contentDescription = null)
            },
            title = { Text(if (result.success) "申請完了" else "エラー") },
            text = { Text(result.message) },
            confirmButton = {
                TextButton(onClick = viewModel::clearApplyResult) { Text("閉じる") }
            },
        )
    }
}

@Composable
private fun InfoSection(title: String, content: @Composable ColumnScope.() -> Unit) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.Bold,
            )
            Spacer(Modifier.height(8.dp))
            content()
        }
    }
}

@Composable
private fun InfoRow(label: String, value: String, emphasize: Boolean = false) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text = value,
            style = if (emphasize) MaterialTheme.typography.titleMedium
                    else MaterialTheme.typography.bodyMedium,
            fontWeight = if (emphasize) FontWeight.Bold else FontWeight.Normal,
            color = if (emphasize) MaterialTheme.colorScheme.primary
                    else MaterialTheme.colorScheme.onSurface,
        )
    }
}

@Composable
private fun ApplySection(
    hasFormUrl: Boolean,
    isApplying: Boolean,
    onFillPdf: () -> Unit,
    onAutoSubmit: (String) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
            text = "申請する",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )

        // 申請書PDF自動記入（無料）
        Button(
            onClick = onFillPdf,
            enabled = hasFormUrl && !isApplying,
            modifier = Modifier.fillMaxWidth(),
        ) {
            if (isApplying) {
                CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
                Spacer(Modifier.width(8.dp))
            }
            Text("申請書PDFを自動記入（無料）")
        }

        if (!hasFormUrl) {
            Text(
                text = "この物件の申請書PDFは現在未登録です。区のページからダウンロードしてください。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }

        // 自動申請（プレミアム）
        OutlinedButton(
            onClick = { /* TODO: Google Play Billing → トークン取得後に onAutoSubmit(token) */ },
            enabled = !isApplying,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("自動申請する（プレミアム）")
        }

        Text(
            text = "※ プレミアム機能は現在無料公開中です",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.secondary,
        )
    }
}
