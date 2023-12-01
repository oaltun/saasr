import Button from "@mui/material/Button";
import { useTranslation } from "react-i18next";
import { Link as RouterLink } from "react-router-dom";
import { ReactComponent as ForbiddenSvg } from "../core/assets/403.svg";
import Result from "../core/components/Result";



// ======= //
// RENDER
// ======= //
// MUI page sizes: xs, sm, md, lg, and xl
// when you set a value for one, it is valid for larger page sizes too.
// unless that value for larger is specified too.
const Forbidden = (props: { message?: string; }) => {
  const { t } = useTranslation();
  const message: string = props.message ? props.message : t("common.errors.forbidden.subTitle")
  return (
    <Result
      extra={
        <Button
          color="primary"
          component={RouterLink}
          to={`/${process.env.PUBLIC_URL}/login`}
          variant="contained"
        >
          {t("auth.register.back")}
        </Button>
      }
      image={<ForbiddenSvg />}
      maxWidth="sm"
      subTitle={message + "(35b3d0f8)"}
      title={t("common.errors.unexpected.title")}
    />
  );
};

export default Forbidden;
