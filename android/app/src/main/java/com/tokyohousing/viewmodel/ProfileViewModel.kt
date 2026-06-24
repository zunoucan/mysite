package com.tokyohousing.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.tokyohousing.data.model.ApplicantProfile
import com.tokyohousing.data.repository.ProfileRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: ProfileRepository,
) : ViewModel() {

    val profile: StateFlow<ApplicantProfile> = repository.profileFlow.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5_000),
        ApplicantProfile(),
    )

    fun saveProfile(profile: ApplicantProfile) {
        viewModelScope.launch { repository.saveProfile(profile) }
    }
}
