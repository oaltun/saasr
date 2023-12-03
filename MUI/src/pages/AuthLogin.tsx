import LoadingButton from "@mui/lab/LoadingButton/LoadingButton";
import Box from "@mui/material/Box/Box";
import Button from "@mui/material/Button/Button";
import Grid from "@mui/material/Grid/Grid";
import Link from "@mui/material/Link/Link";
import Paper from "@mui/material/Paper/Paper";
import TextField from "@mui/material/TextField/TextField";
import Typography from "@mui/material/Typography/Typography";
import { useFormik } from "formik";
import { useCallback, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import * as Yup from "yup";
import BoxedLayout from "../core/components/BoxedLayout";
import { useSnackbar } from "../core/contexts/SnackbarProvider";
import { ErrorHandler } from "../core/utils/errorUtils";
import { useAuth } from "../auth/contexts/AuthProvider";
import { LoginInfo } from "../auth/types/loginInfo";

const Login = () => {
  const auth = useAuth();
  const navigate = useNavigate();
  const snackbar = useSnackbar();
  const { t } = useTranslation();

  const logMeOut = useCallback(() => { auth.logout() }, []);
  useEffect(() => {
    logMeOut();
  }, [logMeOut]);

  const handleLogin = (email: string, password: string) => {
    auth.login(email, password)
      .then((loginInfo: LoginInfo | null) => {
        if (loginInfo) {
          const participationCnt = loginInfo.tokenInfo.user.initialTeamParticipationCount ?? 0;
          const invitationCnt = loginInfo.tokenInfo.user.initialTeamInvitationCount ?? 0;
          console.log(loginInfo);
          if (participationCnt + invitationCnt > 0) {
            navigate(`/${process.env.PUBLIC_URL}/team`, { replace: true });
          } else {
            navigate(`/${process.env.PUBLIC_URL}/join`, { replace: true });
          }
        }
      })
      .catch((e: any) => {
        ErrorHandler.handle(snackbar, e, "(8sdfs)")
      });
  };

  const formik = useFormik({
    initialValues: {
      email: "",
      password: "",
    },
    validationSchema: Yup.object({
      email: Yup.string()
        .email(t("common.validations.email"))
        .required(t("common.validations.required")),
      password: Yup.string()
        .min(8, t("common.validations.min", { size: 8 }))
        .required(t("common.validations.required")),
    }),
    onSubmit: (values) => handleLogin(values.email, values.password),
  });

  return (
    <Grid container component="main" sx={{ height: "100vh" }}>

      <Grid
        item
        xs={false}
        sm={4}
        md={7}
        sx={{
          backgroundImage: "url(./img/startup.svg)",
          backgroundRepeat: "no-repeat",
          bgcolor: "background.default",
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      />
      <Grid item xs={12} sm={8} md={5} component={Paper} square>
        <BoxedLayout>

          <Typography component="h1" variant="h5">
            {t("auth.login.title")}

          </Typography>
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
              label={t("auth.login.form.email.label")}
              name="email"
              autoComplete="email"
              autoFocus
              disabled={auth.isLoggingIn}
              value={formik.values.email}
              onChange={formik.handleChange}
              error={formik.touched.email && Boolean(formik.errors.email)}
              helperText={formik.touched.email && formik.errors.email}
            />
            <TextField
              margin="normal"

              required
              fullWidth
              name="password"
              label={t("auth.login.form.password.label")}
              type="password"
              id="password"
              autoComplete="current-password"
              disabled={auth.isLoggingIn}
              value={formik.values.password}
              onChange={formik.handleChange}
              error={formik.touched.password && Boolean(formik.errors.password)}
              helperText={formik.touched.password && formik.errors.password}
            />
            <Box sx={{ textAlign: "right" }}>
              <Link
                component={RouterLink}
                to={`/${process.env.PUBLIC_URL}/forgot-password`}
                variant="body2"
              >
                {t("auth.login.forgotPasswordLink")}
              </Link>
            </Box>
            <LoadingButton
              type="submit"
              fullWidth
              loading={auth.isLoggingIn}
              variant="contained"
              sx={{ mt: 3 }}
            >
              {t("auth.login.submit")}
            </LoadingButton>
            <Button
              component={RouterLink}
              to={`/${process.env.PUBLIC_URL}/register`}
              color="primary"
              fullWidth
              sx={{ mt: 2 }}
            >
              {t("auth.login.newAccountLink")}
            </Button>
          </Box>
        </BoxedLayout>
      </Grid>
    </Grid>
  );
};

export default Login;
