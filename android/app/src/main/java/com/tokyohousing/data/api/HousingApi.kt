package com.tokyohousing.data.api

import com.tokyohousing.data.model.ApplyRequest
import com.tokyohousing.data.model.ApplyResponse
import com.tokyohousing.data.model.HousingListing
import com.tokyohousing.data.model.Ward
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface HousingApi {

    @GET("api/v1/listings/wards/")
    suspend fun getWards(): List<Ward>

    @GET("api/v1/listings/")
    suspend fun getListings(
        @Query("ward_code") wardCode: String? = null,
        @Query("min_rent") minRent: Int? = null,
        @Query("max_rent") maxRent: Int? = null,
        @Query("layout") layout: String? = null,
        @Query("min_area") minArea: Float? = null,
        @Query("active_only") activeOnly: Boolean = true,
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0,
    ): List<HousingListing>

    @GET("api/v1/listings/{id}")
    suspend fun getListing(@Path("id") id: Int): HousingListing

    @POST("api/v1/apply/submit")
    suspend fun submitApplication(@Body request: ApplyRequest): ApplyResponse

    @POST("api/v1/apply/fill-pdf")
    suspend fun fillPdf(
        @Query("listing_id") listingId: Int,
        @Body profileData: Map<String, String>,
    ): Response<ResponseBody>
}
