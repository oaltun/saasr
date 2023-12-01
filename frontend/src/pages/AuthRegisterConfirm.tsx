import LoadingButton from "@mui/lab/LoadingButton/LoadingButton";
import Box from "@mui/material/Box/Box";
import Button from "@mui/material/Button/Button";
import TextField from "@mui/material/TextField/TextField";
import Typography from "@mui/material/Typography/Typography";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import BoxedLayout from "../core/components/BoxedLayout";
import { useSnackbar } from "../core/contexts/SnackbarProvider";
import { ErrorHandler } from "../core/utils/errorUtils";
import { EmailVerifyPayload, useAuthVerify } from "../saasrapi";

const RegisterConfirm = () => {
  const snackbar = useSnackbar();
  const { t } = useTranslation();
  const [hash, setHash] = useState("");
  const [disableTextField, setDisableTextField] = useState(false);

  const verifyMT = useAuthVerify();

  const verify = (hash: string) => {
    const data: EmailVerifyPayload = { hash: hash };
    verifyMT.mutate(
      { data },
      {
        onError(error) {
          ErrorHandler.handle(snackbar, error, "Error verifying email");
        },
        onSuccess() {
          snackbar.info("Email verified successfully. You can now log in.");
          setDisableTextField(false);
        },
      }
    );
  };

  function handleSubmit(e: React.FormEvent<HTMLInputElement>) {
    verify(hash);
    e.preventDefault();
  }

  return (
    <BoxedLayout>
      <Typography component="h1" variant="h5">
        {t("auth.registerConfirm.title")}
      </Typography>
      <Typography marginTop={3}>
        {t("auth.registerConfirm.subTitle")}
      </Typography>
      <Box component="form" marginTop={3} onSubmit={handleSubmit}>
        <TextField
          margin="normal"
          required
          fullWidth
          id="code"
          label={t("auth.registerConfirm.form.code.label")}
          name="code"
          autoFocus
          disabled={verifyMT.isLoading || disableTextField}
          // value={formik.values.code}
          onChange={(e) => setHash(e.target.value)}
          // error={formik.touched.code && Boolean(formik.errors.code)}
          // helperText={formik.touched.code && formik.errors.code}
        />

        <LoadingButton
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          disabled={disableTextField}
          loading={verifyMT.isLoading}
          sx={{ mt: 2 }}
        >
          {t("auth.registerConfirm.form.action")}
        </LoadingButton>
        <Button
          component={Link}
          to={`/${process.env.PUBLIC_URL}/login`}
          color="primary"
          fullWidth
          sx={{ mt: 2 }}
        >
          {t("auth.registerConfirm.form.back")}
        </Button>
      </Box>
    </BoxedLayout>
  );
};

export default RegisterConfirm;
