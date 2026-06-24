package com.tokyohousing.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Ward(
    val id: Int,
    val code: String,
    @SerialName("name_ja") val nameJa: String,
    @SerialName("website_url") val websiteUrl: String,
    @SerialName("application_url") val applicationUrl: String? = null,
    @SerialName("last_scraped_at") val lastScrapedAt: String? = null,
)

@Serializable
data class HousingListing(
    val id: Int,
    @SerialName("ward_code") val wardCode: String,
    val name: String,
    val address: String,
    @SerialName("building_type") val buildingType: String? = null,
    val floor: String? = null,
    @SerialName("room_number") val roomNumber: String? = null,
    @SerialName("floor_area_sqm") val floorAreaSqm: Float? = null,
    val layout: String? = null,
    @SerialName("year_built") val yearBuilt: Int? = null,
    @SerialName("floor_level") val floorLevel: Int? = null,
    @SerialName("rent_yen") val rentYen: Int? = null,
    @SerialName("management_fee_yen") val managementFeeYen: Int? = null,
    @SerialName("deposit_yen") val depositYen: Int? = null,
    @SerialName("key_money_yen") val keyMoneyYen: Int? = null,
    @SerialName("application_start") val applicationStart: String? = null,
    @SerialName("application_end") val applicationEnd: String? = null,
    @SerialName("move_in_date") val moveInDate: String? = null,
    @SerialName("lottery_date") val lotteryDate: String? = null,
    @SerialName("eligibility_conditions") val eligibilityConditions: String? = null,
    @SerialName("detail_url") val detailUrl: String? = null,
    @SerialName("application_form_url") val applicationFormUrl: String? = null,
    @SerialName("is_active") val isActive: Boolean = true,
) {
    val totalMonthlyYen: Int
        get() = (rentYen ?: 0) + (managementFeeYen ?: 0)
}

@Serializable
data class ApplyRequest(
    @SerialName("listing_id") val listingId: Int,
    val profile: ApplicantProfile,
    @SerialName("premium_token") val premiumToken: String? = null,
)

@Serializable
data class ApplyResponse(
    val success: Boolean,
    val method: String,
    val message: String,
    @SerialName("receipt_number") val receiptNumber: String? = null,
    @SerialName("pdf_base64") val pdfBase64: String? = null,
)

@Serializable
data class ApplicantProfile(
    @SerialName("full_name") val fullName: String = "",
    @SerialName("full_name_kana") val fullNameKana: String = "",
    @SerialName("birth_date") val birthDate: String = "",    // YYYY-MM-DD
    val gender: String = "",
    @SerialName("postal_code") val postalCode: String = "",
    val address: String = "",
    val phone: String = "",
    val email: String = "",
    @SerialName("household_members") val householdMembers: Int = 1,
    @SerialName("income_yen") val incomeYen: Int = 0,
    @SerialName("currently_renting") val currentlyRenting: Boolean = false,
    val occupation: String = "",
    val workplace: String = "",
)
