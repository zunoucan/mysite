package com.tokyohousing.data.repository

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import com.tokyohousing.data.model.ApplicantProfile
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ProfileRepository @Inject constructor(
    private val dataStore: DataStore<Preferences>,
) {
    companion object {
        val KEY_FULL_NAME = stringPreferencesKey("full_name")
        val KEY_FULL_NAME_KANA = stringPreferencesKey("full_name_kana")
        val KEY_BIRTH_DATE = stringPreferencesKey("birth_date")
        val KEY_GENDER = stringPreferencesKey("gender")
        val KEY_POSTAL_CODE = stringPreferencesKey("postal_code")
        val KEY_ADDRESS = stringPreferencesKey("address")
        val KEY_PHONE = stringPreferencesKey("phone")
        val KEY_EMAIL = stringPreferencesKey("email")
        val KEY_HOUSEHOLD = intPreferencesKey("household_members")
        val KEY_INCOME = intPreferencesKey("income_yen")
        val KEY_RENTING = booleanPreferencesKey("currently_renting")
        val KEY_OCCUPATION = stringPreferencesKey("occupation")
        val KEY_WORKPLACE = stringPreferencesKey("workplace")
    }

    val profileFlow: Flow<ApplicantProfile> = dataStore.data.map { prefs ->
        ApplicantProfile(
            fullName = prefs[KEY_FULL_NAME] ?: "",
            fullNameKana = prefs[KEY_FULL_NAME_KANA] ?: "",
            birthDate = prefs[KEY_BIRTH_DATE] ?: "",
            gender = prefs[KEY_GENDER] ?: "",
            postalCode = prefs[KEY_POSTAL_CODE] ?: "",
            address = prefs[KEY_ADDRESS] ?: "",
            phone = prefs[KEY_PHONE] ?: "",
            email = prefs[KEY_EMAIL] ?: "",
            householdMembers = prefs[KEY_HOUSEHOLD] ?: 1,
            incomeYen = prefs[KEY_INCOME] ?: 0,
            currentlyRenting = prefs[KEY_RENTING] ?: false,
            occupation = prefs[KEY_OCCUPATION] ?: "",
            workplace = prefs[KEY_WORKPLACE] ?: "",
        )
    }

    suspend fun saveProfile(profile: ApplicantProfile) {
        dataStore.edit { prefs ->
            prefs[KEY_FULL_NAME] = profile.fullName
            prefs[KEY_FULL_NAME_KANA] = profile.fullNameKana
            prefs[KEY_BIRTH_DATE] = profile.birthDate
            prefs[KEY_GENDER] = profile.gender
            prefs[KEY_POSTAL_CODE] = profile.postalCode
            prefs[KEY_ADDRESS] = profile.address
            prefs[KEY_PHONE] = profile.phone
            prefs[KEY_EMAIL] = profile.email
            prefs[KEY_HOUSEHOLD] = profile.householdMembers
            prefs[KEY_INCOME] = profile.incomeYen
            prefs[KEY_RENTING] = profile.currentlyRenting
            prefs[KEY_OCCUPATION] = profile.occupation
            prefs[KEY_WORKPLACE] = profile.workplace
        }
    }
}
