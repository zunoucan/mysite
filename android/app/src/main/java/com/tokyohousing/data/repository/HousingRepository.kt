package com.tokyohousing.data.repository

import com.tokyohousing.data.api.HousingApi
import com.tokyohousing.data.model.ApplicantProfile
import com.tokyohousing.data.model.ApplyRequest
import com.tokyohousing.data.model.ApplyResponse
import com.tokyohousing.data.model.HousingListing
import com.tokyohousing.data.model.Ward
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val cause: Throwable? = null) : Result<Nothing>()
}

@Singleton
class HousingRepository @Inject constructor(
    private val api: HousingApi,
) {
    suspend fun getWards(): Result<List<Ward>> = safeCall { api.getWards() }

    suspend fun getListings(
        wardCode: String? = null,
        minRent: Int? = null,
        maxRent: Int? = null,
        layout: String? = null,
        minArea: Float? = null,
    ): Result<List<HousingListing>> = safeCall {
        api.getListings(
            wardCode = wardCode,
            minRent = minRent,
            maxRent = maxRent,
            layout = layout,
            minArea = minArea,
        )
    }

    suspend fun getListing(id: Int): Result<HousingListing> = safeCall { api.getListing(id) }

    suspend fun submitApplication(
        listingId: Int,
        profile: ApplicantProfile,
        premiumToken: String? = null,
    ): Result<ApplyResponse> = safeCall {
        api.submitApplication(ApplyRequest(listingId, profile, premiumToken))
    }

    private suspend fun <T> safeCall(block: suspend () -> T): Result<T> =
        withContext(Dispatchers.IO) {
            try {
                Result.Success(block())
            } catch (e: Exception) {
                Result.Error(e.message ?: "通信エラーが発生しました", e)
            }
        }
}
