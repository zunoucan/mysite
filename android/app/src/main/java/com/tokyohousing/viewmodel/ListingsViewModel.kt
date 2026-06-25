package com.tokyohousing.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.tokyohousing.data.model.HousingListing
import com.tokyohousing.data.model.Ward
import com.tokyohousing.data.repository.HousingRepository
import com.tokyohousing.data.repository.Result
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ListingsUiState(
    val listings: List<HousingListing> = emptyList(),
    val wards: List<Ward> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val selectedWardCode: String? = null,
    val minRent: Int? = null,
    val maxRent: Int? = null,
    val selectedLayout: String? = null,
    val sortBy: String? = null,   // null=新着順, rent_asc, rent_desc, end_date_asc, area_desc
)

@HiltViewModel
class ListingsViewModel @Inject constructor(
    private val repository: HousingRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(ListingsUiState())
    val uiState: StateFlow<ListingsUiState> = _uiState.asStateFlow()

    init {
        loadWards()
        loadListings()
    }

    private fun loadWards() {
        viewModelScope.launch {
            when (val result = repository.getWards()) {
                is Result.Success -> _uiState.update { it.copy(wards = result.data) }
                is Result.Error -> {}
            }
        }
    }

    fun loadListings() {
        _uiState.update { it.copy(isLoading = true, error = null) }
        viewModelScope.launch {
            val state = _uiState.value
            when (val result = repository.getListings(
                wardCode = state.selectedWardCode,
                minRent = state.minRent,
                maxRent = state.maxRent,
                layout = state.selectedLayout,
                sortBy = state.sortBy,
            )) {
                is Result.Success -> _uiState.update {
                    it.copy(listings = result.data, isLoading = false)
                }
                is Result.Error -> _uiState.update {
                    it.copy(error = result.message, isLoading = false)
                }
            }
        }
    }

    fun setWardFilter(wardCode: String?) {
        _uiState.update { it.copy(selectedWardCode = wardCode) }
        loadListings()
    }

    fun setRentFilter(min: Int?, max: Int?) {
        _uiState.update { it.copy(minRent = min, maxRent = max) }
        loadListings()
    }

    fun setLayoutFilter(layout: String?) {
        _uiState.update { it.copy(selectedLayout = layout) }
        loadListings()
    }

    fun setSortBy(sortBy: String?) {
        _uiState.update { it.copy(sortBy = sortBy) }
        loadListings()
    }

    fun applyFilters(layout: String?, minRent: Int?, maxRent: Int?, sortBy: String?) {
        _uiState.update { it.copy(
            selectedLayout = layout,
            minRent = minRent,
            maxRent = maxRent,
            sortBy = sortBy,
        )}
        loadListings()
    }

    fun clearFilters() {
        _uiState.update { it.copy(
            selectedWardCode = null, minRent = null, maxRent = null,
            selectedLayout = null, sortBy = null,
        )}
        loadListings()
    }
}
