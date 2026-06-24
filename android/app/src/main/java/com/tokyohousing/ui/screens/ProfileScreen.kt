package com.tokyohousing.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.tokyohousing.data.model.ApplicantProfile
import com.tokyohousing.viewmodel.ProfileViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(viewModel: ProfileViewModel = hiltViewModel()) {
    val saved by viewModel.profile.collectAsState()
    var draft by remember(saved) { mutableStateOf(saved) }
    var saved_snack by remember { mutableStateOf(false) }
    val snackState = remember { SnackbarHostState() }

    LaunchedEffect(saved_snack) {
        if (saved_snack) {
            snackState.showSnackbar("プロフィールを保存しました")
            saved_snack = false
        }
    }

    Scaffold(
        topBar = { TopAppBar(title = { Text("プロフィール登録") }) },
        snackbarHost = { SnackbarHost(snackState) },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = {
                    viewModel.saveProfile(draft)
                    saved_snack = true
                },
                text = { Text("保存") },
                icon = {},
            )
        }
    ) { padding ->
        Column(
            Modifier
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            SectionHeader("基本情報")
            ProfileField("氏名（漢字）", draft.fullName) {
                draft = draft.copy(fullName = it)
            }
            ProfileField("氏名（ふりがな）", draft.fullNameKana) {
                draft = draft.copy(fullNameKana = it)
            }
            ProfileField("生年月日（YYYY-MM-DD）", draft.birthDate) {
                draft = draft.copy(birthDate = it)
            }

            SectionHeader("性別")
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                listOf("男", "女", "その他").forEach { g ->
                    FilterChip(
                        selected = draft.gender == g,
                        onClick = { draft = draft.copy(gender = g) },
                        label = { Text(g) },
                    )
                }
            }

            SectionHeader("連絡先")
            ProfileField("郵便番号（ハイフンなし）", draft.postalCode, KeyboardType.Number) {
                draft = draft.copy(postalCode = it)
            }
            ProfileField("住所", draft.address) { draft = draft.copy(address = it) }
            ProfileField("電話番号", draft.phone, KeyboardType.Phone) {
                draft = draft.copy(phone = it)
            }
            ProfileField("メールアドレス", draft.email, KeyboardType.Email) {
                draft = draft.copy(email = it)
            }

            SectionHeader("世帯・収入")
            ProfileField(
                label = "世帯人数",
                value = draft.householdMembers.toString(),
                keyboardType = KeyboardType.Number,
            ) { draft = draft.copy(householdMembers = it.toIntOrNull() ?: 1) }
            ProfileField(
                label = "年間収入（円）",
                value = draft.incomeYen.toString(),
                keyboardType = KeyboardType.Number,
            ) { draft = draft.copy(incomeYen = it.toIntOrNull() ?: 0) }

            Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                Text("現在賃貸住宅に居住中")
                Spacer(Modifier.weight(1f))
                Switch(
                    checked = draft.currentlyRenting,
                    onCheckedChange = { draft = draft.copy(currentlyRenting = it) },
                )
            }

            SectionHeader("職業")
            ProfileField("職業・職種", draft.occupation) { draft = draft.copy(occupation = it) }
            ProfileField("勤務先名称", draft.workplace) { draft = draft.copy(workplace = it) }

            Spacer(Modifier.height(72.dp)) // FAB の後ろにコンテンツが隠れないよう
        }
    }
}

@Composable
private fun SectionHeader(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.titleSmall,
        color = MaterialTheme.colorScheme.primary,
        modifier = Modifier.padding(top = 8.dp),
    )
}

@Composable
private fun ProfileField(
    label: String,
    value: String,
    keyboardType: KeyboardType = KeyboardType.Text,
    onValueChange: (String) -> Unit,
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        keyboardOptions = KeyboardOptions(keyboardType = keyboardType),
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
    )
}
