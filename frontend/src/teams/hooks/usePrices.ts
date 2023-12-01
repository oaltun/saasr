import { useQuery } from "@tanstack/react-query";
import { mergeKeys } from "../../core/utils/mapUtils";
import { subscriptionPriceList } from "../../saasrapi";

const fetchPrices = async () => {
  const prices = await subscriptionPriceList();
  const priceMap: Map<string, number> = new Map();
  for (const pricing of prices.data) {
    priceMap.set(
      mergeKeys(pricing.plan_id, pricing.billing_cycle_id),
      pricing.price_per_month
    );
  }
  return { prices: prices.data, priceMap: priceMap };
};
export function usePrices() {
  return useQuery({
    queryKey: ["subscription prices"],
    queryFn: fetchPrices,
  });
}
