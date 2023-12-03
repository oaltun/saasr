import { mergeKeys } from "../../core/utils/mapUtils";

export const totalPriceA = (pricePerMonth: number, count: number, months: number) => {
    return (
        pricePerMonth
        * count
        * months).toFixed(2);
}

export const totalPrice = (priceQry, cycleQry, cycleId, planId, nLicenses) => {
    return totalPriceA(
        priceQry.data?.priceMap.get(mergeKeys(planId, cycleId))!
        , parseInt(nLicenses)
        , cycleQry.data!.billingCycleMap!.get(cycleId)!.billing_period_in_months);
}