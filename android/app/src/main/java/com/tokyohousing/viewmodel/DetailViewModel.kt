package com.tokyohousing.viewmodel

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.tokyohousing.data.model.ApplicantProfile
import com.tokyohousing.data.model.ApplyResponse
import com.tokyohousing.data.model.HousingListing
import com.tokyohousing.data.repository.HousingRepository
import com.tokyohousing.data.repository.ProfileRepository
import com.tokyohousing.data.repository.Result
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class DetailUiState(
    val listing: HousingListing? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val applyResult: ApplyResponse? = null,
    val isApplying: Boolean = false,
)

@HiltViewModel
class DetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val housingRepo: HousingRepository,
    private val profileRepo: ProfileRepository,
) : ViewModel() {

    private val listingId: Int = checkNotNull(savedStateHandle["listingId"])

    private val _uiState = MutableStateFlow(DetailUiState())
    val uiState: StateFlow<DetailUiState> = _uiState.asStateFlow()

    init {
        loadListing()
    }

    private fun loadListing() {
        _uiState.update { it.copy(isLoading = true) }
        viewModelScope.launch {
            when (val result = housingRepo.getListing(listingId)) {
                is Result.Success -> _uiState.update {
                    it.copy(listing = result.data, isLoading = false)
                }
                is Result.Error -> _uiState.update {
                    it.copy(error = result.message, isLoading = false)
                }
            }
        }
    }

    fun apply(premiumToken: String? = null) {
        _uiState.update { it.copy(isApplying = true, applyResult = null) }
        viewModelScope.launch {
            val profile = profileRepo.profileFlow.first()
            when (val result = housingRepo.submitApplication(listingId, profile, premiumToken)) {
                is Result.Success -> _uiState.update {
                    it.copy(applyResult = result.data, isApplying = false)
                }
                is Result.Error -> _uiState.update {
                    it.copy(error = result.message, isApplying = false)
                }
            }
        }
    }

    fun clearApplyResult() {
        _uiState.update { it.copy(applyResult = null) }
    }
}
