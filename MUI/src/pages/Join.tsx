import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import { Alert, CircularProgress, Grid, TextField } from "@mui/material/";
import { useState } from "react";
import Button from "@mui/material/Button";
import Stepper from "@mui/material/Stepper";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Typography from "@mui/material/Typography";
import Checkbox from "@mui/material/Checkbox";
import { useNavigate } from "react-router-dom";
import { paymentRequestURL } from "../core/config/urls.js";
import axios, { AxiosError } from "axios";
import { getToken } from "../auth/utils/auth";
import Pluralize from "pluralize";

import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { useSnackbar } from "../core/contexts/SnackbarProvider";

import Logo from "../core/components/Logo";
import { GridRow } from "../core/components/GridRow";
import { GridCol } from "../core/components/GridCol";
import { GridPage } from "../core/components/GridPage";
import { PricingSelector } from "../join/components/PricingSelector";
import { mergeKeys } from "../core/utils/mapUtils";
import { totalPrice } from "../join/utils/totalPrice";
import { usePrices } from "../teams/hooks/usePrices";
import { usePlans } from "../teams/hooks/usePlans";
import { useBillingCycles } from "../teams/hooks/useBillingCycles";
import { ErrorHandler } from "../core/utils/errorUtils";
import { billingPeriodInMonths } from "../join/utils/billingPeriodInMonths";
import Result from "../core/components/Result";
import { GridSection } from "../core/components/GridSection";
import { GridBr } from "../core/components/GridBr";
import { PrevNext } from "../join/components/PrevNext";

const stepMap = {
  plan: "Plan Details",
  buyer: "Buyer Information",
  payment: "Payment Method",
  billing: "Billing Address",
  company: "Company",
  confirm: "Confirm",
};

const stepKeys = ["plan", "buyer", "payment", "billing", "company", "confirm"];

// stepper steps
const steps = [
  "Plan Details",
  "Buyer Information",
  "Payment Method",
  "Billing Address",
  "Company",
  "Confirm",
];

//---- important initial values
const initial = {
  billingCycleId: "4_months",
  planId: "lite",
  pricePerPeriodPerLicense: 5.49,
};

const debug = false;

//---- the component start
const Join = () => {
  const navigate = useNavigate();
  const snackbar = useSnackbar();

  //---- Start of payment info --------------
  //---- payment

  const [payment_numberOfLicenses, set_payment_numberOfLicenses] =
    useState("1");
  const [payment_billingCycleId, set_payment_billingCycleId] = useState(
    initial.billingCycleId
  );
  const [payment_planId, set_payment_planId] = useState(initial.planId);
  //---- payment.buyer
  const [payment_buyer_name, set_payment_buyer_name] = useState(
    debug ? "oğuz" : ""
  );
  const [payment_buyer_surname, set_payment_buyer_surname] = useState(
    debug ? "altun" : ""
  );
  const [payment_buyer_gsmNumber, set_payment_buyer_gsmNumber] = useState(
    debug ? "05068449618" : ""
  );
  //---- payment.buyer.address
  const [payment_buyer_address_country, set_payment_buyer_address_country] =
    useState(debug ? "Turkey" : "");
  const [payment_buyer_address_state, set_payment_buyer_address_state] =
    useState("");
  const [payment_buyer_address_city, set_payment_buyer_address_city] = useState(
    debug ? "istanbul" : ""
  );
  const [
    payment_buyer_address_streetAddress,
    set_payment_buyer_address_streetAddress,
  ] = useState(debug ? "gencosman mah. davutpaşa sok." : "");
  const [
    payment_buyer_address_postalCode,
    set_payment_buyer_address_postalCode,
  ] = useState(debug ? "23222" : "");
  //---- payment.payment_card
  const [
    payment_paymentCard_cardHolderName,
    set_payment_paymentCard_cardHolderName,
  ] = useState(debug ? "oguz altun" : "");
  const [payment_paymentCard_cardNumber, set_payment_paymentCard_cardNumber] =
    useState(debug ? "5400010000000004" : "");
  const [payment_paymentCard_expireYear, set_payment_paymentCard_expireYear] =
    useState(debug ? "25" : "");
  const [payment_paymentCard_expireMonth, set_payment_paymentCard_expireMonth] =
    useState(debug ? "10" : "");
  const [payment_paymentCard_cvc, set_payment_paymentCard_cvc] = useState(
    debug ? "123" : ""
  );
  const [
    payment_paymentCard_registerCard,
    set_payment_paymentCard_registerCard,
  ] = useState(0);
  //---- payment.billing_address
  const [payment_billingAddress_country, set_payment_billingAddress_country] =
    useState(debug ? "Turkey" : "");
  const [payment_billingAddress_state, set_payment_billingAddress_state] =
    useState("");
  const [payment_billingAddress_city, set_payment_billingAddress_city] =
    useState(debug ? "istanbul" : "");
  const [
    payment_billingAddress_streetAddress,
    set_payment_billingAddress_streetAddress,
  ] = useState(debug ? "gencosman mah. davutpaşa sok." : "");
  const [
    payment_billingAddress_postalCode,
    set_payment_billingAddress_postalCode,
  ] = useState(debug ? "23222" : "");
  //---- payment.company_info
  const [
    payment_userIsCompanyRepresenter,
    set_payment_userIsCompanyRepresenter,
  ] = useState(false);
  const [payment_companyInfo_companyName, set_payment_companyInfo_companyName] =
    useState("");
  const [
    payment_companyInfo_companyTaxNumber,
    set_payment_companyInfo_companyTaxNumber,
  ] = useState("");
  const [
    payment_companyInfo_companyTaxOffice,
    set_payment_companyInfo_companyTaxOffice,
  ] = useState("");
  //---- payment.company_info.address
  const [
    payment_companyInfo_address_country,
    set_payment_companyInfo_address_country,
  ] = useState("");
  const [
    payment_companyInfo_address_state,
    set_payment_companyInfo_address_state,
  ] = useState("");
  const [
    payment_companyInfo_address_city,
    set_payment_companyInfo_address_city,
  ] = useState("");
  const [
    payment_companyInfo_address_streetAddress,
    set_payment_companyInfo_address_streetAddress,
  ] = useState("");
  const [
    payment_companyInfo_address_postalCode,
    set_payment_companyInfo_address_postalCode,
  ] = useState("");
  const [
    payment_userAgreesToTermsAndConditions,
    set_payment_userAgreesToTermsAndConditions,
  ] = useState(false);

  //---- End of payment info --------------

  //---- step controls -------------------
  const [activeStep, setActiveStep] = useState(0);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
  };

  //---- form controls ----------------------
  const [form_cardHolderNameVisible, set_form_cardHolderNameVisible] =
    useState(false);
  const [form_buyerAddressVisible, set_form_buyerAddressVisible] =
    useState(false);
  const [form_companyAddressVisible, set_form_companyAddressVisible] =
    useState(false);
  const [form_addSeparateCompanyAddress, set_form_addSeparateCompanyAddress] =
    useState(false);
  const [form_buyerChecked, set_form_buyerChecked] = useState(false);

  //-- Queries
  const priceQry = usePrices();
  const planQry = usePlans();
  const cycleQry = useBillingCycles();

  //-- utility functions

  const makePayment = async () => {
    // do some data controls:
    if (payment_paymentCard_registerCard !== 1) {
      ErrorHandler.handle(
        snackbar,
        "Please accept saving of your billing information to continue.",
        "(n9998)"
      );
      return;
    }
    if (!payment_userAgreesToTermsAndConditions) {
      ErrorHandler.handle(
        snackbar,
        "Please agree to SAASR's  terms of service,  license terms,  and  privacy policy to continue.",
        "(n7998)"
      );
      return;
    }

    const payment_data = {
      price: totalPrice(
        priceQry,
        cycleQry,
        payment_billingCycleId,
        payment_planId,
        payment_numberOfLicenses
      ),
      user_agrees_to_terms_and_conditions:
        payment_userAgreesToTermsAndConditions,
      number_of_licenses: payment_numberOfLicenses,
      billing_cycle_id: payment_billingCycleId,
      plan_id: payment_planId,
      buyer: {
        name: payment_buyer_name,
        surname: payment_buyer_surname,
        gsm_number: payment_buyer_gsmNumber,
        address: {
          country: payment_buyer_address_country,
          state: payment_buyer_address_state,
          city: payment_buyer_address_city,
          street_address: payment_buyer_address_streetAddress,
          postal_code: payment_buyer_address_postalCode,
        },
      },
      payment_card: {
        cardHolderName: payment_paymentCard_cardHolderName,
        cardNumber: payment_paymentCard_cardNumber,
        expireYear: payment_paymentCard_expireYear,
        expireMonth: payment_paymentCard_expireMonth,
        cvc: payment_paymentCard_cvc,
        registerCard: payment_paymentCard_registerCard,
      },
      billing_address: {
        country: payment_billingAddress_country,
        state: payment_billingAddress_state,
        city: payment_billingAddress_city,
        street_address: payment_billingAddress_streetAddress,
        postal_code: payment_billingAddress_postalCode,
      },
      user_is_company_representer: payment_userIsCompanyRepresenter,
      company_info: {
        company_name: payment_companyInfo_companyName,
        company_tax_number: payment_companyInfo_companyTaxNumber,
        company_tax_office: payment_companyInfo_companyTaxOffice,
        address: {
          country: payment_companyInfo_address_country,
          state: payment_companyInfo_address_state,
          city: payment_companyInfo_address_city,
          street_address: payment_companyInfo_address_streetAddress,
          postal_code: payment_companyInfo_address_postalCode,
        },
      },
    };

    const token = getToken();
    const config = {
      headers: { Authorization: `Bearer ${token}` },
    };

    try {
      const response = await axios.post(
        paymentRequestURL,
        payment_data,
        config
      );
      const url = `${process.env.PUBLIC_URL}/team`;
      console.log([
        "Payment done.",
        "url:",
        url,
        "PUBLIC_URL",
        process.env.PUBLIC_URL,
      ]);
      navigate(url);
    } catch (error: any) {
      ErrorHandler.handle(snackbar, error, "(n9998)");
    }
  };

  // ================ //
  // RENDER FUNCTIONS
  // ================ //

  // MUI page sizes: xs, sm, md, lg, and xl
  // when you set a value for one, it is valid for larger page sizes too.
  // unless that value for larger is specified too.

  function StepperHeader() {
    return (
      <GridSection justifyContent="center" xs={12} lg={8}>
        <GridRow justifyContent="center">
          <GridCol xs={5} justifyContent="center">
            <Toolbar
              sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              <Logo sx={{ mt: 2 }} />
            </Toolbar>
          </GridCol>
        </GridRow>

        <GridRow justifyContent="center">
          <GridCol xs={12} justifyContent="center">
            <Typography variant="h5" mb={3}>
              Select your subscription details to join
            </Typography>
          </GridCol>
        </GridRow>

        <GridRow justifyContent="center" xs={12}>
          <Stepper activeStep={activeStep} alternativeLabel>
            {stepKeys.map((label, index) => {
              const stepProps: { completed?: boolean } = {};
              const labelProps: {
                optional?: React.ReactNode;
              } = {};

              return (
                <Step key={stepMap[label]} {...stepProps}>
                  <StepLabel {...labelProps}>{stepMap[label]}</StepLabel>
                </Step>
              );
            })}
          </Stepper>
        </GridRow>
      </GridSection>
    );
  }

  type BuyerInformationProps = {};
  function BuyerInformation(props: BuyerInformationProps) {
    return (
      <GridSection justifyContent="center">
        <GridRow justifyContent="center">
          <Typography variant="h6" mb={3}>
            Buyer Information
          </Typography>
        </GridRow>

        <GridRow>
          <Grid item xs>
            <TextField
              label="Name"
              value={payment_buyer_name}
              id="paymentBuyerName"
              onChange={(e) => {
                set_payment_buyer_name(e.target.value);
                set_payment_paymentCard_cardHolderName(e.target.value);
              }}
              fullWidth
              required
            />
          </Grid>
          <Grid item xs>
            <TextField
              label="Surname"
              value={payment_buyer_surname}
              id="paymentBuyerSurname"
              onChange={(e) => {
                set_payment_buyer_surname(e.target.value);
              }}
              fullWidth
              required
            />
          </Grid>
        </GridRow>
        <GridRow>
          <Grid item xs>
            <TextField
              label="Phone Number"
              id="PhoneNumber"
              value={payment_buyer_gsmNumber}
              onChange={(e) => {
                set_payment_buyer_gsmNumber(e.target.value);
              }}
              fullWidth
              required
            />
          </Grid>
        </GridRow>
      </GridSection>
    );
  }

  function PaymentCard() {
    return (
      <GridSection>
        <GridRow justifyContent="center">
          <Typography variant="h6" mt={3} mb={3}>
            Payment Method
          </Typography>
        </GridRow>
        <GridRow mb={4}>
          <GridCol xs={12}>
            <TextField
              label="Card Number"
              value={payment_paymentCard_cardNumber}
              onChange={(e) => {
                set_payment_paymentCard_cardNumber(e.target.value);
              }}
              fullWidth
              required
            />
          </GridCol>
        </GridRow>

        <GridRow justifyContent="space-between">
          <GridCol xs={6}>
            <GridCol xs={6}>
              <TextField
                label="MM"
                value={payment_paymentCard_expireMonth}
                onChange={(e) => {
                  set_payment_paymentCard_expireMonth(e.target.value);
                }}
                fullWidth
                required
              />
            </GridCol>
            <GridCol xs={6}>
              <TextField
                label="YY"
                value={payment_paymentCard_expireYear}
                onChange={(e) => {
                  set_payment_paymentCard_expireYear(e.target.value);
                }}
                fullWidth
                required
              />
            </GridCol>
          </GridCol>

          <GridCol xs={4}>
            <TextField
              label="CCV"
              value={payment_paymentCard_cvc}
              onChange={(e) => {
                set_payment_paymentCard_cvc(e.target.value);
              }}
              fullWidth
              required
            />
          </GridCol>
        </GridRow>
      </GridSection>
    );
  }

  function BillingAddress() {
    return (
      <Grid item container spacing={2} xs={12} justifyContent="center">
        <Grid item container justifyContent={"center"} xs={11}>
          <Typography variant="h6">Billing Address (Card Address)</Typography>
        </Grid>
        <Grid item xs={11} md={8}>
          <TextField
            label="Street Address"
            value={payment_billingAddress_streetAddress}
            onChange={(e) => {
              set_payment_billingAddress_streetAddress(e.target.value);
              set_payment_buyer_address_streetAddress(e.target.value);
            }}
            multiline
            fullWidth
            required
          />
        </Grid>
        <Grid item xs={11} md={8}>
          <TextField
            label="City"
            value={payment_billingAddress_city}
            onChange={(e) => {
              set_payment_billingAddress_city(e.target.value);
              set_payment_buyer_address_city(e.target.value);
            }}
            fullWidth
            required
          />
        </Grid>
        <Grid item xs={11} md={8}>
          <TextField
            label="Country"
            value={payment_billingAddress_country}
            onChange={(e) => {
              set_payment_billingAddress_country(e.target.value);
              set_payment_buyer_address_country(e.target.value);
            }}
            fullWidth
            required
          />
        </Grid>
        <Grid item container xs={11} md={8} justifyContent="space-between">
          <Grid item xs={6}>
            <TextField
              label="State/Province/Region"
              value={payment_billingAddress_state}
              onChange={(e) => {
                set_payment_billingAddress_state(e.target.value);
                set_payment_buyer_address_state(e.target.value);
              }}
              fullWidth
            />
          </Grid>

          <Grid item xs={5.9}>
            <TextField
              label="Postal/Zip Code"
              value={payment_billingAddress_postalCode}
              onChange={(e) => {
                set_payment_billingAddress_postalCode(e.target.value);
                set_payment_buyer_address_postalCode(e.target.value);
              }}
              fullWidth
              required
            />
          </Grid>
        </Grid>
      </Grid>
    );
  }

  function Company() {
    return (
      <Grid item container spacing={2} xs={12} justifyContent="center">
        <Grid item container justifyContent={"center"} xs={11}>
          <Typography variant="h6">Company (If Exists)</Typography>
        </Grid>
        <Grid item xs={11} md={8}>
          <TextField
            label="Company Name"
            value={payment_companyInfo_companyName}
            onChange={(e) => {
              set_payment_companyInfo_companyName(e.target.value);
            }}
            fullWidth
          />
        </Grid>

        <Grid
          item
          container
          spacing={2}
          justifyContent={"space-between"}
          xs={11}
          md={8}
        >
          <Grid item xs={6}>
            <TextField
              label="Company Tax Office"
              value={payment_companyInfo_companyTaxOffice}
              onChange={(e) => {
                set_payment_companyInfo_companyTaxOffice(e.target.value);
              }}
              fullWidth
            />
          </Grid>
          <Grid item xs>
            <TextField
              label="Company Tax Number"
              value={payment_companyInfo_companyTaxNumber}
              onChange={(e) => {
                set_payment_companyInfo_companyTaxNumber(e.target.value);
              }}
              fullWidth
            />
          </Grid>
        </Grid>
      </Grid>
    );
  }

  function OrderSummaryGrid() {
    if (planQry.data && priceQry.data) {
      const numLicenses = parseInt(payment_numberOfLicenses);
      const billingPeriod = billingPeriodInMonths(
        cycleQry,
        payment_billingCycleId
      );
      const planName = planQry.data.planMap.get(payment_planId)!.name;
      const pricePPeriod = priceQry.data.priceMap.get(
        mergeKeys(payment_planId, payment_billingCycleId)
      )!;
      const totalPriceVal = totalPrice(
        priceQry,
        cycleQry,
        payment_billingCycleId,
        payment_planId,
        payment_numberOfLicenses
      );
      return (
        <GridSection justifyContent="center">
          <GridRow justifyContent="center">
            <Typography variant="h6" mb={2}>
              Order Summary
            </Typography>
          </GridRow>
          <GridRow xs={12} justifyContent="center">
            <GridCol sx={{ xs: 10, sm: 8, md: 8, lg: 6 }}>
              <Grid item xs={6}>
                Number of Licenses:
              </Grid>
              <Grid item xs={6}>
                {Pluralize("license", numLicenses, true)}
              </Grid>
              <Grid item xs={6}>
                Billing period:
              </Grid>
              <Grid item xs={6}>
                {Pluralize("month", billingPeriod, true)}
              </Grid>

              <Grid item xs={6}>
                Plan:
              </Grid>
              <Grid item xs={6}>
                {planName} Plan
              </Grid>

              <Grid item xs={6}>
                Unit Price:
              </Grid>
              <Grid item xs={6}>
                {" "}
                ${pricePPeriod} / License / Month
              </Grid>

              <Grid item xs={6}>
                <Typography variant="h6">Total Price:</Typography>
              </Grid>

              <Grid item xs={6}>
                <Typography variant="h6">
                  ${totalPriceVal} / License / Month
                </Typography>
              </Grid>
            </GridCol>
          </GridRow>
          <GridRow xs={12} justifyContent="right">
            <GridCol xs={8}>
              <Grid item>
                <Checkbox
                  checked={
                    payment_paymentCard_registerCard === 1 ? true : false
                  }
                  onChange={(e) => {
                    set_payment_paymentCard_registerCard(
                      e.target.checked ? 1 : 0
                    );
                  }}
                />
                &nbsp; Save my information for recurring billing.
                <GridBr />
                <Checkbox
                  checked={payment_userAgreesToTermsAndConditions}
                  onChange={(e) => {
                    set_payment_userAgreesToTermsAndConditions(
                      e.target.checked
                    );
                  }}
                />
                &nbsp; I agree to SAASR's &nbsp;
                <a
                  target="_blank"
                  rel="noreferrer"
                  href="https://example.com/tos/"
                >
                  terms of service
                </a>
                , &nbsp;
                <a
                  target="_blank"
                  rel="noreferrer"
                  href="https://example.com/license_terms/"
                >
                  license terms
                </a>
                , &nbsp; and &nbsp;
                <a
                  target="_blank"
                  rel="noreferrer"
                  href="https://example.com/privacy/"
                >
                  privacy policy
                </a>
                .
              </Grid>
            </GridCol>
          </GridRow>
        </GridSection>
      );
    }
    if (priceQry.isError || planQry.isError) {
      const error: AxiosError = priceQry.error as AxiosError;
      return <Result title={error.message} />;
    }

    return <CircularProgress />;
  }

  function Finished() {
    return (
      <Grid item xs={12}>
        <Typography sx={{ mt: 2, mb: 1 }}>
          All steps completed - you&apos;re finished
        </Typography>

        <br />
        <Button onClick={() => handleReset()}>Reset</Button>
      </Grid>
    );
  }

  function Page() {
    return (
      <GridPage justifyContent="center">
        <StepperHeader />

        {activeStep === 0 && (
          <PrevNext
            activeStep={activeStep}
            handleBack={handleBack}
            handleNext={handleNext}
            makePayment={makePayment}
            steps={steps}
          >
            <PricingSelector
              numLicensesInit={payment_numberOfLicenses}
              billingCycleIdInit={payment_billingCycleId}
              planIdInit={payment_planId}
              onNumberOfLicensesChange={set_payment_numberOfLicenses}
              onBillingCycleIdChange={set_payment_billingCycleId}
              onPlanIdChange={set_payment_planId}
            />
          </PrevNext>
        )}

        {activeStep === 1 && (
          <PrevNext
            activeStep={activeStep}
            handleBack={handleBack}
            handleNext={handleNext}
            makePayment={makePayment}
            steps={steps}
          >
            <BuyerInformation />
          </PrevNext>
        )}

        {activeStep === 2 && (
          <PrevNext
            activeStep={activeStep}
            handleBack={handleBack}
            handleNext={handleNext}
            makePayment={makePayment}
            steps={steps}
          >
            {PaymentCard()}
          </PrevNext>
        )}

        {activeStep === 3 && (
          <PrevNext
            activeStep={activeStep}
            handleBack={handleBack}
            handleNext={handleNext}
            makePayment={makePayment}
            steps={steps}
          >
            {BillingAddress()}
          </PrevNext>
        )}

        {activeStep === 4 && (
          <PrevNext
            activeStep={activeStep}
            handleBack={handleBack}
            handleNext={handleNext}
            makePayment={makePayment}
            steps={steps}
          >
            {Company()}
          </PrevNext>
        )}

        {activeStep === 5 && (
          <PrevNext
            activeStep={activeStep}
            handleBack={handleBack}
            handleNext={handleNext}
            makePayment={makePayment}
            steps={steps}
          >
            {OrderSummaryGrid()}
          </PrevNext>
        )}
      </GridPage>
    );
  }

  // MUI page sizes: xs, sm, md, lg, and xl
  // when you set a value for one, it is also valid for larger page
  // sizes, unless that value for larger is specified.
  if (cycleQry.data && planQry.data && priceQry.data) {
    return Page();
  }
  if (priceQry.isError) {
    console.log("Error, (0d1c42e8)");

    return (
      <Box>
        <>Error getting prices: {priceQry.error}</>
      </Box>
    );
  }
  if (planQry.isError) {
    console.log("Error, (9caf3bbe)");

    return (
      <Box>
        <>Error getting plans: {planQry.error}</>
      </Box>
    );
  }
  if (cycleQry.isError) {
    console.log("Error, (9765928d)");

    return (
      <Box>
        <>Error getting billing cycles: {cycleQry.error}</>
      </Box>
    );
  }
  return <CircularProgress />;
};

export default Join;
