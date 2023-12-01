export const billingPeriodInMonths = (cycleQry, billingCycleId) => {
    return cycleQry.data!.billingCycleMap.get(billingCycleId)!.billing_period_in_months;
}