import { Navigate, useLocation, Outlet } from "react-router-dom";
import { isEndpointPermitted, getDefaultPage } from "../../utils/authorization.ts";
import { useAxiosInterceptors } from "../../hooks";
import { useAuth } from "../../hooks";

const PrivateRoute = () => {
    const authContext = useAuth();
    if (!authContext) {
        throw new Error("Не определено значение для конекста авторизации");
    }
    const { currentUser } = authContext;
    const { pathname } = useLocation();
    useAxiosInterceptors(); // при невалидном токене переадресация в логин
    return isEndpointPermitted(currentUser, pathname) ? (
        <Outlet />
    ) : (
        <Navigate to={getDefaultPage(currentUser)} />
    );
};

export default PrivateRoute;
