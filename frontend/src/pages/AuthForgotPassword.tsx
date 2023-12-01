import { useFormik } from "formik";
import { useTranslation } from "react-i18next";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import * as Yup from "yup";
import BoxedLayout from "../core/components/BoxedLayout";
import { useSnackbar } from "../core/contexts/SnackbarProvider";
import { useState } from "react";
import { forgotPassword } from "../auth/utils/auth";
import Typography from "@mui/material/Typography/Typography";
import Box from "@mui/material/Box/Box";
import TextField from "@mui/material/TextField/TextField";
import LoadingButton from "@mui/lab/LoadingButton/LoadingButton";
import Button from "@mui/material/Button/Button";
import { ErrorHandler } from "../core/utils/errorUtils";

const ForgotPassword = () => {
  const navigate = useNavigate();
  const snackbar = useSnackbar();
  const { t } = useTranslation();
  const [isLoading, setIsLoading] = useState(false);

  const formik = useFormik({
    initialValues: {
      email: "",
    },
    validationSchema: Yup.object({
      email: Yup.string()
        .email(t("common.validations.email"))
        .required(t("common.validations.required")),
    }),
    onSubmit: ({ email }) => handleForgotPassword(email),
  });

  const handleForgotPassword = async (email: string) => {
    setIsLoading(true);
    forgotPassword({ email })
      .then(() => {
        setIsLoading(false);
        snackbar.success(t("auth.forgotPassword.notifications.success"));
        navigate(`/${process.env.PUBLIC_URL}/forgot-password-confirm`);
      })
      .catch((e) => {
        console.log("Error, (b126c05a)");

        setIsLoading(false);
        console.log('e', e);
        ErrorHandler.handle(snackbar, e, "Error sending email to forgot password endpoint")
      });
  };

  return (
    <BoxedLayout>
      <Typography component="h1" variant="h5">
        {t("auth.forgotPassword.title")}
      </Typography>
      <Typography marginTop={3}>{t("auth.forgotPassword.subTitle")}</Typography>
      <Box
        component="form"
        marginTop={3}
        noValidate
        onSubmit={formik.handleSubmit}
      >
        <TextField
          margin="normal"
          required
          fullWidth
          id="email"
          label={t("auth.forgotPassword.form.email.label")}
          name="email"
          autoComplete="email"
          autoFocus
          disabled={isLoading}
          value={formik.values.email}
          onChange={formik.handleChange}
          error={formik.touched.email && Boolean(formik.errors.email)}
          helperText={formik.touched.email && formik.errors.email}
        />
        <LoadingButton
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          disabled={isLoading}
          loading={isLoading}
          sx={{ mt: 2 }}
        >
          {t("auth.forgotPassword.form.action")}
        </LoadingButton>
        <Button
          component={RouterLink}
          to={`/${process.env.PUBLIC_URL}/login`}
          color="primary"
          fullWidth
          sx={{ mt: 2 }}
        >
          {t("auth.forgotPassword.form.back")}
        </Button>
      </Box>
    </BoxedLayout>
  );
};

export default ForgotPassword;
