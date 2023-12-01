import Box from "@mui/material/Box/Box";
import CircularProgress from "@mui/material/CircularProgress/CircularProgress";
import Grid from "@mui/material/Grid/Grid";
import TextField from "@mui/material/TextField/TextField";
import ToggleButton from "@mui/material/ToggleButton/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup/ToggleButtonGroup";
import Typography from "@mui/material/Typography/Typography";
import { AxiosError } from "axios";
import { Fragment, useState } from "react";
import Result from "../../core/components/Result";
import { mergeKeys } from "../../core/utils/mapUtils";
import { BillingCycle } from "../../saasrapi/model/billingCycle";
import { Plan } from "../../saasrapi/model/plan";
import { useBillingCycles } from "../../teams/hooks/useBillingCycles";
import { usePlans } from "../../teams/hooks/usePlans";
import { usePrices } from "../../teams/hooks/usePrices";
import { GridRow } from "../../core/components/GridRow";
import { GridSection } from "../../core/components/GridSection";
import Pluralize from "pluralize";
import { totalPrice, totalPriceA } from "../utils/totalPrice";
import { billingPeriodInMonths } from "../utils/billingPeriodInMonths";

import { PropsWithChildren } from "react";
import { GridCol } from "../../core/components/GridCol";
import { GridBr } from "../../core/components/GridBr";

type Props = {
  numLicensesInit: any;
  billingCycleIdInit: string;
  planIdInit: string;
  onNumberOfLicensesChange: any;
  onBillingCycleIdChange: any;
  onPlanIdChange: any;
};

export const PricingSelector = ({
  numLicensesInit,
  billingCycleIdInit,
  planIdInit,
  onNumberOfLicensesChange,
  onBillingCycleIdChange,
  onPlanIdChange,
}: Props) => {
  const [numberOfLicenses, setNumberOfLicensesLocal] =
    useState(numLicensesInit);
  const [billingCycleId, setBillingCycleIdLocal] = useState(billingCycleIdInit);
  const [planId, setPlanIdLocal] = useState(planIdInit);

  const priceQry = usePrices();
  const planQry = usePlans();
  const cycleQry = useBillingCycles();

  function set_payment_numberOfLicenses(val: string) {
    setNumberOfLicensesLocal(val);
    onNumberOfLicensesChange(val);
  }
  function set_payment_billingCycleId(val: string) {
    setBillingCycleIdLocal(val);
    onBillingCycleIdChange(val);
  }
  function set_payment_planId(val: string) {
    setPlanIdLocal(val);
    onPlanIdChange(val);
  }
  const handleNumberOfLicencesChange = (e: { target: { value: string } }) => {
    if (parseInt(e.target.value) > 0) {
      set_payment_numberOfLicenses(e.target.value);
    }
    if (e.target.value === "") {
      set_payment_numberOfLicenses("");
    }
  };

  const handleNumberOfLicencesFieldBlur = (e: {
    target: { value: string };
  }) => {
    if (parseInt(e.target.value) > 0) {
      set_payment_numberOfLicenses(e.target.value);
    } else {
      set_payment_numberOfLicenses("1");
    }
  };

  function TotalPricing() {
    const pricePerMonth = priceQry.data?.priceMap.get(
      mergeKeys(planId, billingCycleId)
    );
    const months =
      cycleQry.data?.billingCycleMap?.get(
        billingCycleId
      )?.billing_period_in_months;

    if (pricePerMonth && months) {
      return (
        <GridRow justifyContent="center">
          <Typography sx={{ fontWeight: "bold", mt: 2 }}>
            Period price: $
            {totalPriceA(pricePerMonth, parseInt(numberOfLicenses), months)}
          </Typography>
          <GridBr />
          <Typography>
            (
            {Pluralize(
              "month",
              billingPeriodInMonths(cycleQry, billingCycleId),
              true
            )}{" "}
            * {Pluralize("license", parseInt(numberOfLicenses), true)} * $
            {priceQry.data?.priceMap.get(mergeKeys(planId, billingCycleId))} /
            month / licence )
          </Typography>
        </GridRow>
      );
    }
    return <CircularProgress />;
  }

  if (priceQry.data && cycleQry.data && planQry.data) {
    return (
      <GridSection justifyContent="center">
        <GridRow justifyContent="center">
          <GridCol xs={3}>
            <Typography variant="h6">Number of Licences:</Typography>
          </GridCol>
          <GridCol xs={1.2}>
            <TextField
              value={numberOfLicenses}
              onChange={(e) => handleNumberOfLicencesChange(e)}
              onBlur={(e) => handleNumberOfLicencesFieldBlur(e)}
              type="number"
              hiddenLabel={true}
              fullWidth
              size="small"
            />
          </GridCol>
        </GridRow>

        <GridRow justifyContent="center">
          <Typography sx={{ fontWeight: "bold", mt: 2, mb: 2 }}>
            Billing period:
          </Typography>
          &nbsp;
          <ToggleButtonGroup>
            {cycleQry.data?.billingCycles.map(
              (billingCycle: BillingCycle, idx) => (
                <ToggleButton
                  key={idx}
                  id={`radio-${idx}`}
                  value={billingCycle.id}
                  selected={billingCycleId === billingCycle.id}
                  onClick={(_e, v) => set_payment_billingCycleId(v)}
                >
                  {billingCycle.name}
                </ToggleButton>
              )
            )}
          </ToggleButtonGroup>
        </GridRow>

        <ToggleButtonGroup>
          {planQry.data?.plans.map((plan: Plan, idx) => (
            <Grid item sm={12} md={4} key={plan.id}>
              <ToggleButton
                sx={{ p: 1, m: 1 }}
                key={idx}
                id={`plan-${idx}`}
                value={plan.id}
                disabled={plan.id === "free"}
                selected={planId === plan.id}
                onClick={(_e, v) => set_payment_planId(v)}
              >
                <Box display="flex" flexDirection="column">
                  {plan.id === "free"
                    ? plan.name
                    : "Select " + plan.name + " Plan"}
                  <Typography
                    sx={{
                      fontWeight: "bold",
                      mt: 2,
                      mb: 1,
                    }}
                  >
                    {plan.id === "free"
                      ? "$0"
                      : "$" +
                        priceQry.data.priceMap.get(
                          mergeKeys(plan.id, billingCycleId)
                        ) +
                        " / month /license"}
                  </Typography>
                  <SplitFeatures
                    str={plan.features}
                    plus={plan.id !== "free"}
                  />
                </Box>
              </ToggleButton>
            </Grid>
          ))}
        </ToggleButtonGroup>

        <TotalPricing />
      </GridSection>
    );
  }

  if (priceQry.isError || cycleQry.isError || planQry.isError) {
    const error: AxiosError = priceQry.error as AxiosError;
    return <Result title={error.message} />;
  }

  return <CircularProgress />;
};

type SplitFeaturesProps = {
  str: string;
  plus: boolean;
};

function SplitFeatures({ str, plus }: SplitFeaturesProps) {
  const f = str.split("--");

  return (
    <Fragment>
      {f.map((feature, index) => {
        return (
          <Typography key={feature}>
            {plus && index !== 0 ? "+ " : ""}
            {feature.trim()}.
          </Typography>
        );
      })}
    </Fragment>
  );
}
