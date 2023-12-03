import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useFormik } from "formik";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";
import * as Yup from "yup";
import BoxedLayout from "../core/components/BoxedLayout";
import { useSnackbar } from "../core/contexts/SnackbarProvider";
import { useRegister } from "../auth/hooks/useRegister";
import { useState } from "react";


import { UserInput } from "../auth/types/userInput"
import { signUp } from "../auth/utils/auth";
import { ErrorHandler } from "../core/utils/errorUtils";
import LoadingButton from "@mui/lab/LoadingButton/LoadingButton";


const Register = () => {
  const snackbar = useSnackbar();
  const { t } = useTranslation();
  const navigate = useNavigate();


  const [password, setPassword] = useState<string>("");
  const [passwordConfirmation, setPasswordConfirmation] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [error, setError] = useState<string>("");

  const { isRegistering, register } = useRegister();



  const formik = useFormik({
    initialValues: {
      email: "",
      password: "",
      passwordConfirmation: "",
    },
    validationSchema: Yup.object({
      email: Yup.string()
        .email("Invalid email address")
        .required(t("common.validations.required")),
      password: Yup.string()
        .max(20, t("common.validations.max", { size: 20 }))
        .required(t("common.validations.required")),
      passwordConfirmation: Yup.string()
        .max(20, t("common.validations.max", { size: 20 }))
        .required(t("common.validations.required")),
    }),
    onSubmit: (values) => handleSignUp(values),
  });

  const handleSignUp = async (values: UserInput) => {
    console.log("(a765j)");
    // Password confirmation validation
    if (password !== passwordConfirmation) {
      console.log("(b765j)");
      setError("Passwords do not match (917a4e05)");
    } else {
      console.log("(c765j)");
      setError("");
      try {
        console.log("(d765j)");

        const data = await signUp(values);
        console.log("(e765j)");

        if (data) {
          console.log("(f765j)");
          snackbar.success('Verify your email to be able to login.');
        }
        navigate(`/${process.env.PUBLIC_URL}/register-confirm`, { replace: true });
      } catch (err: any) {
        ErrorHandler.handle(snackbar, err, "(hgj73)")
      }
    }
  };

  return (
    <BoxedLayout>
      <Typography component="h1" variant="h5">
        {t("auth.register.title")}
      </Typography>
      <Box
        component="form"
        marginTop={3}
        noValidate
        onSubmit={formik.handleSubmit}
      >
        <TextField
          name="email"
          id="email"
          autoComplete="email"
          label={t("auth.register.form.email.label")}
          disabled={isRegistering}
          value={formik.values.email}
          onChange={formik.handleChange}
          error={formik.touched.email && Boolean(formik.errors.email)}
          helperText={formik.touched.email && formik.errors.email}
          margin="normal"
          required
          fullWidth
          autoFocus
        />
        <TextField
          name="password"
          id="password"
          type="password"
          label={t("auth.register.form.pass.label")}
          margin="normal"
          required
          fullWidth
          disabled={isRegistering}
          value={formik.values.password}
          onChange={formik.handleChange}
          error={formik.touched.password && Boolean(formik.errors.password)}
          helperText={formik.touched.password && formik.errors.password}
        />
        <TextField
          id="passwordConfirmation"
          name="passwordConfirmation"
          label={t("auth.register.form.passAgain.label")}
          margin="normal"
          required
          fullWidth
          type="password"
          disabled={isRegistering}
          value={formik.values.passwordConfirmation}
          onChange={formik.handleChange}
          error={
            formik.touched.passwordConfirmation &&
            Boolean(formik.errors.passwordConfirmation)
          }
          helperText={
            formik.touched.passwordConfirmation &&
            formik.errors.passwordConfirmation
          }
        />

        <LoadingButton
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          disabled={isRegistering}
          loading={isRegistering}
          sx={{ mt: 2 }}
        >
          {t("auth.register.submit")}
        </LoadingButton>
        <Button
          component={Link}
          to={`/${process.env.PUBLIC_URL}/login`}
          color="primary"
          fullWidth
          sx={{ mt: 2 }}
        >
          {t("auth.register.back")}
        </Button>
      </Box>
    </BoxedLayout>
  );
};

export default Register;
