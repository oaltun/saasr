import Button from "@mui/material/Button";
import { useTranslation } from "react-i18next";
import { Link as RouterLink } from "react-router-dom";
import Result from "../core/components/Result";
import { ReactComponent as NotFoundSvg } from "../core/assets/404.svg";



// ======= //
// RENDER
// ======= //
// MUI page sizes: xs, sm, md, lg, and xl
// when you set a value for one, it is valid for larger page sizes too.
// unless that value for larger is specified too.
const NotFound = () => {
  const { t } = useTranslation();

  return (
    <Result
      extra={
        <Button
          color="secondary"
          component={RouterLink}
          to={`/${process.env.PUBLIC_URL}/login`}
          variant="contained"
        >
          {t("common.backHome")}
        </Button>
      }
      image={<NotFoundSvg />}
      maxWidth="sm"
      subTitle={t("common.errors.notFound.subTitle")}
      title={t("common.errors.notFound.title")}
    />
  );
};

export default NotFound;
