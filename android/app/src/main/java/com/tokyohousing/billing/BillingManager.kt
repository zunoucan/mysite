package com.tokyohousing.billing

import android.app.Activity
import android.content.Context
import com.android.billingclient.api.*
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.suspendCancellableCoroutine
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.coroutines.resume

const val PRODUCT_AUTO_SUBMIT = "auto_submit_monthly"

enum class PremiumState { LOADING, FREE, PREMIUM }

@Singleton
class BillingManager @Inject constructor(
    @ApplicationContext private val context: Context,
) : PurchasesUpdatedListener {

    private val _premiumState = MutableStateFlow(PremiumState.LOADING)
    val premiumState: StateFlow<PremiumState> = _premiumState.asStateFlow()

    private var purchaseToken: String? = null

    private val billingClient = BillingClient.newBuilder(context)
        .setListener(this)
        .enablePendingPurchases(
            PendingPurchasesParams.newBuilder().enableOneTimeProducts().build()
        )
        .build()

    init {
        billingClient.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(result: BillingResult) {
                if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                    queryPurchases()
                } else {
                    _premiumState.value = PremiumState.FREE
                }
            }

            override fun onBillingServiceDisconnected() {
                _premiumState.value = PremiumState.FREE
            }
        })
    }

    private fun queryPurchases() {
        billingClient.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.INAPP)
                .build()
        ) { result, purchases ->
            if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                val activePurchase = purchases.firstOrNull { purchase ->
                    purchase.products.contains(PRODUCT_AUTO_SUBMIT) &&
                        purchase.purchaseState == Purchase.PurchaseState.PURCHASED
                }
                purchaseToken = activePurchase?.purchaseToken
                _premiumState.value = if (activePurchase != null) PremiumState.PREMIUM else PremiumState.FREE
            } else {
                _premiumState.value = PremiumState.FREE
            }
        }
    }

    suspend fun launchBillingFlow(activity: Activity): Boolean {
        val productList = listOf(
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(PRODUCT_AUTO_SUBMIT)
                .setProductType(BillingClient.ProductType.INAPP)
                .build()
        )
        val params = QueryProductDetailsParams.newBuilder().setProductList(productList).build()

        return suspendCancellableCoroutine { cont ->
            billingClient.queryProductDetailsAsync(params) { result, productDetailsList ->
                if (result.responseCode != BillingClient.BillingResponseCode.OK || productDetailsList.isEmpty()) {
                    cont.resume(false)
                    return@queryProductDetailsAsync
                }
                val productDetails = productDetailsList[0]
                val offerToken = productDetails.oneTimePurchaseOfferDetails
                    ?: run { cont.resume(false); return@queryProductDetailsAsync }

                val flowParams = BillingFlowParams.newBuilder()
                    .setProductDetailsParamsList(
                        listOf(
                            BillingFlowParams.ProductDetailsParams.newBuilder()
                                .setProductDetails(productDetails)
                                .build()
                        )
                    )
                    .build()
                val flowResult = billingClient.launchBillingFlow(activity, flowParams)
                cont.resume(flowResult.responseCode == BillingClient.BillingResponseCode.OK)
            }
        }
    }

    fun getPurchaseToken(): String? = purchaseToken

    override fun onPurchasesUpdated(result: BillingResult, purchases: List<Purchase>?) {
        if (result.responseCode == BillingClient.BillingResponseCode.OK && purchases != null) {
            purchases.forEach { purchase ->
                if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED) {
                    purchaseToken = purchase.purchaseToken
                    _premiumState.value = PremiumState.PREMIUM
                    // サーバー側でも検証するため API にトークンを送信
                    acknowledgePurchase(purchase)
                }
            }
        }
    }

    private fun acknowledgePurchase(purchase: Purchase) {
        if (purchase.isAcknowledged) return
        val params = AcknowledgePurchaseParams.newBuilder()
            .setPurchaseToken(purchase.purchaseToken)
            .build()
        billingClient.acknowledgePurchase(params) { /* ignore result */ }
    }
}
